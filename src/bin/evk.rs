use clap::{Parser, Subcommand};
use anyhow::{Result, Context};
use std::fs::File;
use std::io::Read;
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
    Verify { 
        file: PathBuf 
    },
    Pack {
        #[arg(long)]
        job: String,
        #[arg(long)]
        snapshot: String,
        #[arg(long)]
        input: PathBuf,
        #[arg(long)]
        output: PathBuf,
    },
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
        Commands::Pack { job, snapshot, input, output } => {
            // Create a ZIP file at the output path
            let zip_file = File::create(&output).context("Failed to create .evkp file")?;
            let mut zip = ZipWriter::new(zip_file);
            
            // Add metadata
            let metadata = json!({
                "job": job,
                "snapshot": snapshot,
                "timestamp": Utc::now().to_rfc3339(),
                "version": "1.0"
            });
            
            let metadata_str = serde_json::to_string_pretty(&metadata)?;
            zip.start_file("metadata.json", FileOptions::default())?;
            zip.write_all(metadata_str.as_bytes())?;
            
            println!("✓ Created .evkp bundle: {}", output.display());
        }
    }
    Ok(())
}
