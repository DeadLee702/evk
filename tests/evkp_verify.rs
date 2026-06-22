use sha2::{Sha256, Digest};
use std::fs;
use std::io::Read;
use zip::ZipArchive;

#[test]
#[ignore = "Requires fixtures/sample.evkp to be present"]
fn evkp_verify_manifest_and_hashes() -> anyhow::Result<()> {
    let evkp_path = "fixtures/sample.evkp"; // put a test bundle here
    let zip_file = fs::File::open(evkp_path)?;
    let mut zip = ZipArchive::new(zip_file)?;

    // 1. Load manifest.json
    let manifest_str = {
        let mut manifest_file = zip.by_name("manifest.json")?;
        let mut s = Vec::new();
        manifest_file.read_to_end(&mut s)?;
        String::from_utf8(s)?
    }; // manifest_file dropped here, zip borrow ends

    let manifest: serde_json::Value = serde_json::from_str(&manifest_str)?;

    // 2. Verify manifest_hash
    let mut manifest_no_hash = manifest.clone();
    manifest_no_hash.as_object_mut().unwrap().remove("manifest_hash");
    let canonical = serde_json::to_string(&manifest_no_hash)?; // must match your canonical rules
    let computed_hash = format!("sha256:{:x}", Sha256::digest(canonical.as_bytes()));
    assert_eq!(manifest["manifest_hash"], computed_hash, "manifest_hash mismatch");

    // 3. Verify each file hash in order
    let files = manifest["files"].as_array().unwrap();
    for entry in files {
        let path = entry["path"].as_str().unwrap();
        let expected_hash = entry["hash"].as_str().unwrap();

        let mut file = zip.by_name(path)?;
        let mut buf = Vec::new();
        file.read_to_end(&mut buf)?;
        let actual_hash = format!("sha256:{:x}", Sha256::digest(&buf));

        assert_eq!(expected_hash, actual_hash, "hash mismatch for {}", path);
    }

    // 4. Verify order array matches files array
    let order = manifest["order"].as_array().unwrap();
    assert_eq!(order.len(), files.len(), "order length mismatch");

    Ok(())
}
