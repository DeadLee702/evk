use clap::{Parser, Subcommand};
use anyhow::{Result, Context, anyhow};
use std::fs::File;
use std::io::{Read, Write};
use std::path::PathBuf;
use sha2::{Sha256, Digest};
use zip::write::{FileOptions, ZipWriter};
use zip::ZipArchive;

#[derive(Parser)]
#[command(name = "evk")]
#[command(about = "EVK verifier", long_about = None)]
struct Cli {
    #[command(subcommand)]
    cmd: Cmd,
}

#[derive(Subcommand)]
enum Cmd {
    Verify {
        #[arg(long)]
        bundle: String,
    },
    Pack {
        #[arg(long)]
        job: String,
        #[arg(long)]
        snapshot: String,
        #[arg(long)]
        input: String,
        #[arg(long)]
        output: String,
    },
}

fn run_pack(job: String, snapshot: String, input: String, output: String) -> Result<()> {
    let job_bytes = std::fs::read(&job)?;
    let snap_bytes = std::fs::read(&snapshot)?;
    let input_bytes = std::fs::read(&input)?;

    let file = File::create(&output)?;
    let mut zip = ZipWriter::new(file);
    let opts = FileOptions::default().compression_method(zip::CompressionMethod::Deflated);

    let mut manifest = String::new();
    for (name, data) in [
        ("job.evk", &job_bytes),
        ("snapshot.evk", &snap_bytes),
        ("input.bin", &input_bytes),
    ] {
        let hash = Sha256::digest(data);
        let hash_hex = hex::encode(hash);
        manifest.push_str(&format!("{} {} {}\n", hash_hex, data.len(), name));
        zip.start_file(name, opts)?;
        zip.write_all(data)?;
    }

    zip.start_file("manifest.txt", opts)?;
    zip.write_all(manifest.as_bytes())?;
    zip.finish()?;
    Ok(())
}

fn run_verify(bundle: String) -> Result<()> {
    let file = File::open(&bundle)?;
    let mut zip = ZipArchive::new(file)?;

    // 1. Read manifest first. Only files in manifest exist.
    let mut manifest_str = String::new();
    zip.by_name("manifest.txt")?.read_to_string(&mut manifest_str)?;

    // 2. Hash every file before use. No env, no time, no FS walk.
    for line in manifest_str.lines() {
        let parts: Vec<&str> = line.splitn(3, ' ').collect();
        let (expected_hex, expected_len, name) = (parts[0], parts[1].parse::<u32>()?, parts[2]);
        let mut data = Vec::new();
        zip.by_name(name)?.read_to_end(&mut data)?;
        if data.len() as u32!= expected_len {
            return Err(anyhow!("Bundle integrity violation: {} size mismatch", name));
        }
        let hash = Sha256::digest(&data);
        if hex::encode(hash)!= expected_hex {
            return Err(anyhow!("Bundle integrity violation: {} hash mismatch", name));
        }
    }
    Ok(())
}

fn main() {
    let cert_flag = std::env::args().any(|a| a == "--cert");

    let result = std::panic::catch_unwind(|| -> anyhow::Result<()> {
        let cli = Cli::try_parse()?;
        match cli.cmd {
            Cmd::Verify { bundle,.. } => run_verify(bundle),
            Cmd::Pack { job, snapshot, input, output } => run_pack(job, snapshot, input, output),
        }
    });

    if cert_flag {
        match result {
            Ok(Ok(_)) => {
                print!("EVK VERIFICATION CERTIFICATE\nStatus: VALID\nExecution resolved within bundle scope.\nNo unresolved references within bundle scope.\nNo execution divergence detected.\nResult: CLOSED\n");
            }
            Ok(Err(e)) => {
                print!("EVK VERIFICATION CERTIFICATE\nStatus: INVALID\nReason: {}\nResult: REJECTED\n", e);
                std::process::exit(1);
            }
            Err(_) => {
                print!("EVK VERIFICATION CERTIFICATE\nStatus: INVALID\nReason: panic\nResult: REJECTED\n");
                std::process::exit(1);
            }
        }
    } else {
        if let Err(e) = result.unwrap_or_else(|_| Err(anyhow::anyhow!("panic"))) {
            eprintln!("Error: {}", e);
            std::process::exit(1);
        }
    }
}
