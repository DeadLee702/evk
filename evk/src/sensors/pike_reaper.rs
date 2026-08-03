use std::{env, sync::Arc, time::Duration};

use anyhow::Context;
use prost::Message;
use rdkafka::{
    producer::{FutureProducer, FutureRecord},
    ClientConfig,
};
use tokio::runtime::Runtime;

use crate::proto::syscall::SyscallEvent;

// Aya imports
use aya::{Bpf, maps::ringbuf::RingBuffer, util::online_cpus};
use aya::programs::TracePoint;

fn kafka_producer() -> Result<FutureProducer, anyhow::Error> {
    let brokers = env::var("KAFKA_BROKERS").unwrap_or_else(|_| "localhost:9092".to_string());
    let producer: FutureProducer = ClientConfig::new()
        .set("bootstrap.servers", &brokers)
        .set("message.timeout.ms", "5000")
        .create()
        .context("creating Kafka producer")?;
    Ok(producer)
}

fn send_to_kafka(producer: &FutureProducer, topic: &str, payload: &[u8]) {
    let record = FutureRecord::to(topic).payload(payload);
    // We spawn a short-lived tokio runtime for sending because this file is synchronous.
    // If your application is already async, integrate accordingly.
    let rt = match Runtime::new() {
        Ok(r) => r,
        Err(e) => panic!("failed to create tokio runtime for kafka send: {:?}", e),
    };
    let send_future = producer.send(record, Duration::from_secs(5));
    if let Err((e, _)) = rt.block_on(send_future) {
        // Non-recoverable for this design: panic as requested
        panic!("kafka send failed: {:?}", e);
    }
}

pub fn run() {
    // Panics on any fatal error as you requested (use anyhow::Context for messages).
    let bpf_path = std::path::Path::new("bpf/pike_reaper.bpf.o");
    let mut bpf = Bpf::load_file(&bpf_path)
        .unwrap_or_else(|e| panic!("failed to load BPF object {:?}: {:?}", bpf_path, e));

    // Attach the tracepoint program if present (the BPF program should be configured accordingly)
    if let Ok(mut prog) = bpf.program_mut("tracepoint__syscalls__sys_enter_execve").and_then(|p| p.try_into::<TracePoint>()) {
        prog.load().unwrap_or_else(|e| panic!("failed to load tracepoint program: {:?}", e));
        prog.attach("syscalls", "sys_enter_execve").unwrap_or_else(|e| {
            panic!("failed to attach tracepoint program to syscalls:sys_enter_execve: {:?}", e)
        });
    }

    // Prepare Kafka producer
    let producer = kafka_producer().unwrap_or_else(|e| panic!("failed to create kafka producer: {:?}", e));
    let topic = env::var("PIKE_REAPER_TOPIC").unwrap_or_else(|_| "evk-syscalls".to_string());

    // RingBuffer consumption
    let mut ringbuf = RingBuffer::try_from(bpf.map_mut("EVENTS").unwrap_or_else(|_| {
        panic!("EVENTS map not found in BPF object; expected ring buffer map named 'EVENTS'")
    })).unwrap_or_else(|e| panic!("failed to open ring buffer map: {:?}", e));

    // Poll loop (blocking)
    loop {
        // The closure receives raw bytes written by the BPF ring buffer consumer.
        let res = ringbuf.poll(Duration::from_secs(1), |data: &[u8]| {
            // Expect protobuf-encoded SyscallEvent from BPF
            match SyscallEvent::decode(data) {
                Ok(mut ev) => {
                    // If needed, enrich the event here (timestamps, host id, etc.)
                    let mut buf = Vec::with_capacity(ev.encoded_len());
                    ev.encode(&mut buf).expect("prost encode should not fail");
                    send_to_kafka(&producer, &topic, &buf);
                }
                Err(e) => {
                    panic!("failed to decode SyscallEvent from BPF ringbuffer: {:?}", e);
                }
            }
        });

        if let Err(e) = res {
            // Poll returned an error we consider fatal in this design
            panic!("ringbuffer poll error: {:?}", e);
        }

        // small sleep to avoid hot-spin if ring buffer is quiet
        std::thread::sleep(Duration::from_millis(10));
    }
}
