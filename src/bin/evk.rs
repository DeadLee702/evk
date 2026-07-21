use anyhow::{bail, Context, Result};
use chrono::{TimeZone, Utc};
use clap::{Parser, Subcommand};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::env;
use std::fs::{self, File};
use std::io::{Read, Write};
use std::path::{Path, PathBuf};
use zip::write::FileOptions;
use zip::{ZipArchive, ZipWriter};

#[derive(Parser)]
#[command(name = "evk", about = "EVK - Evidence Verification Kit")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Verify the manifest and file hashes inside an .evkp bundle.
    Verify {
        #[arg(long)]
        bundle: PathBuf,
        /// Emit a signed-style certificate line on success.
        #[arg(long)]
        cert: bool,
    },
    /// Pack evidence files into an .evkp bundle with a SHA-256 manifest.
    Pack {
        #[arg(long)]
        job: PathBuf,
        #[arg(long)]
        snapshot: PathBuf,
        #[arg(long)]
        input: PathBuf,
        #[arg(long)]
        output: PathBuf,
    },
}

fn sha256_hex(bytes: &[u8]) -> String {
    format!("sha256:{:x}", Sha256::digest(bytes))
}

fn entry_name(path: &Path) -> Result<String> {
    path.file_name()
        .and_then(|n| n.to_str())
        .map(|s| s.to_string())
        .with_context(|| format!("invalid file name: {}", path.display()))
}

fn deterministic_created() -> String {
    match env::var("SOURCE_DATE_EPOCH") {
        Ok(val) => {
            let secs = val.trim().parse::<i64>().unwrap_or(0);
            Utc.timestamp_opt(secs, 0)
                .single()
                .unwrap_or_else(|| Utc.timestamp_opt(0, 0).single().unwrap())
                .to_rfc3339()
        }
        Err(_) => "1970-01-01T00:00:00+00:00".to_string(),
    }
}

fn pack(job: &Path, snapshot: &Path, input: &Path, output: &Path) -> Result<()> {
    let zip_file = File::create(output).context("Failed to create .evkp file")?;
    let mut zip = ZipWriter::new(zip_file);
    let options = FileOptions::default()
        .compression_method(zip::CompressionMethod::Stored)
        .last_modified_time(zip::DateTime::default());

    let mut files = Vec::new();
    let mut order = Vec::new();

    for path in [job, snapshot, input] {
        let bytes = fs::read(path)
            .with_context(|| format!("Failed to read evidence file: {}", path.display()))?;
        let name = entry_name(path)?;
        let hash = sha256_hex(&bytes);

        zip.start_file(&name, options)?;
        zip.write_all(&bytes)?;

        files.push(json!({ "path": name, "hash": hash }));
        order.push(name);
    }

    // manifest_hash is computed over the manifest with the field removed,
    // using serde_json's canonical (sorted-key) serialization.
    let mut manifest = json!({
        "version": "1.0",
        "created": deterministic_created(),
        "files": files,
        "order": order,
    });
    let canonical = serde_json::to_string(&manifest)?;
    let manifest_hash = sha256_hex(canonical.as_bytes());
    manifest
        .as_object_mut()
        .context("manifest is not a JSON object")?
        .insert("manifest_hash".to_string(), json!(manifest_hash));

    let manifest_str = serde_json::to_string_pretty(&manifest)?;
    zip.start_file("manifest.json", options)?;
    zip.write_all(manifest_str.as_bytes())?;

    zip.finish()?;
    println!("Created .evkp bundle: {}", output.display());
    Ok(())
}

fn verify(bundle: &Path, cert: bool) -> Result<()> {
    let file = File::open(bundle)
        .with_context(|| format!("Failed to open bundle: {}", bundle.display()))?;
    let mut zip = ZipArchive::new(file).context("bundle is not a valid .evkp archive")?;

    let manifest_str = {
        let mut manifest_file = zip
            .by_name("manifest.json")
            .context("bundle is missing manifest.json")?;
        let mut s = Vec::new();
        manifest_file.read_to_end(&mut s)?;
        String::from_utf8(s).context("manifest.json is not valid UTF-8")?
    };

    let manifest: Value =
        serde_json::from_str(&manifest_str).context("manifest.json is not valid JSON")?;

    // 1. Verify manifest_hash.
    let mut manifest_no_hash = manifest.clone();
    manifest_no_hash
        .as_object_mut()
        .context("manifest is not a JSON object")?
        .remove("manifest_hash");
    let canonical = serde_json::to_string(&manifest_no_hash)?;
    let computed_hash = sha256_hex(canonical.as_bytes());
    let manifest_hash = manifest
        .get("manifest_hash")
        .and_then(Value::as_str)
        .context("manifest is missing manifest_hash")?;
    if manifest_hash != computed_hash {
        bail!("INVALID: manifest_hash mismatch (expected {computed_hash}, found {manifest_hash})");
    }

    // 2. Verify each file hash in declared order.
    let files = manifest
        .get("files")
        .and_then(Value::as_array)
        .context("manifest is missing files array")?
        .clone();
    for entry in &files {
        let path = entry
            .get("path")
            .and_then(Value::as_str)
            .context("file entry missing path")?;
        let expected = entry
            .get("hash")
            .and_then(Value::as_str)
            .context("file entry missing hash")?;

        let mut f = zip
            .by_name(path)
            .with_context(|| format!("file listed in manifest is missing: {path}"))?;
        let mut buf = Vec::new();
        f.read_to_end(&mut buf)?;
        let actual = sha256_hex(&buf);
        if actual != expected {
            bail!("INVALID: hash mismatch for {path} (expected {expected}, found {actual})");
        }
    }

    // 3. order length must match files length.
    let order_len = manifest
        .get("order")
        .and_then(Value::as_array)
        .context("manifest is missing order array")?
        .len();
    if order_len != files.len() {
        bail!(
            "INVALID: order length ({order_len}) does not match files length ({})",
            files.len()
        );
    }

    let report = json!({
        "bundle": bundle.to_str(),
        "status": "VALID",
        "files_verified": files.len(),
        "manifest_hash": manifest_hash,
        "timestamp": Utc::now().to_rfc3339(),
    });
    println!("{}", serde_json::to_string_pretty(&report)?);

    if cert {
        println!(
            "CERT: {} VALID {} files verified at {}",
            manifest_hash,
            files.len(),
            Utc::now().to_rfc3339()
        );
    }
    Ok(())
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    match cli.command {
        Commands::Verify { bundle, cert } => verify(&bundle, cert),
        Commands::Pack {
            job,
            snapshot,
            input,
            output,
        } => pack(&job, &snapshot, &input, &output),
    }
}
