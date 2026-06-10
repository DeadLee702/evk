use clap::{Parser, Subcommand};
use anyhow::{Result, Context};
use std::fs::File;
use std::io::{Read, Write};
use std::path::PathBuf;
use sha2::{Sha256, Digest};
use zip::write::{FileOptions, ZipWriter};
use serde_json::json;
use chrono::Utc;

#[derive(Parser)]
#[command(name = "evk", about = "Forensic Verification Engine")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    Verify { file: PathBuf },
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Verify { file } => {
            let mut f = File::open(&file).context("Failed to open file")?;
            let mut buffer = Vec::new();
            f.read_to_end(&mut buffer)?;

            let hash = Sha256::digest(&buffer);
            let timestamp = Utc::now().to_rfc3339();

            let report = json!({
                "file": file.to_str(),
                "sha256": format!("{:x}", hash),
                "timestamp": timestamp,
                "status": "verified"
            });

            println!("{}", serde_json::to_string_pretty(&report)?);
        }
    }
    Ok(())
}

