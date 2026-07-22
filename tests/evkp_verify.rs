use assert_cmd::prelude::*;
use assert_fs::TempDir;
use predicates::prelude::*;
use std::fs;
use std::process::Command;

#[test]
fn evkp_verify_manifest_and_hashes_runtime() -> Result<(), Box<dyn std::error::Error>> {
    let temp = TempDir::new()?;
    let job = temp.path().join("job.evk");
    let snapshot = temp.path().join("snapshot.evk");
    let input = temp.path().join("input.bin");
    let evkp_path = temp.path().join("runtime_test.evkp");

    fs::write(&job, b"job payload")?;
    fs::write(&snapshot, b"snapshot payload")?;
    fs::write(&input, b"input payload")?;

    let mut pack = Command::cargo_bin("evk")?;
    pack.args([
        "pack",
        "--job",
        job.to_str().unwrap(),
        "--snapshot",
        snapshot.to_str().unwrap(),
        "--input",
        input.to_str().unwrap(),
        "--output",
        evkp_path.to_str().unwrap(),
    ])
    .assert()
    .success();

    let mut verify = Command::cargo_bin("evk")?;
    verify
        .args(["verify", "--bundle"])
        .arg(&evkp_path)
        .assert()
        .success()
        .stdout(predicate::str::contains("\"status\": \"VALID\""))
        .stdout(predicate::str::contains("\"files_verified\": 3"));

    temp.close()?;
    Ok(())
}
