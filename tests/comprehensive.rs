use evk_lib::{internal_hash, Node};
use sha2::{Digest, Sha256};
use std::fs;
use std::io::Read;
use std::path::PathBuf;
use zip::ZipArchive;

// ─── Merkle tree unit tests ───────────────────────────────────────────

fn leaf(data: &[u8]) -> Node {
    Node::Leaf {
        data: data.to_vec(),
    }
}

fn consistent_internal(children: Vec<Node>) -> Node {
    let hash = internal_hash(&children);
    Node::Internal { hash, children }
}

#[test]
fn leaf_hash_matches_sha256() {
    for input in [b"".as_slice(), b"a", b"hello world", &[0xFF; 32]] {
        let expected: [u8; 32] = Sha256::digest(input).into();
        assert_eq!(leaf(input).get_hash(), expected);
    }
}

#[test]
fn internal_hash_is_concatenation_of_child_hashes() {
    let children = vec![leaf(b"alpha"), leaf(b"beta"), leaf(b"gamma")];
    let mut hasher = Sha256::new();
    for c in &children {
        hasher.update(c.get_hash());
    }
    let expected: [u8; 32] = hasher.finalize().into();
    assert_eq!(internal_hash(&children), expected);
}

#[test]
fn single_leaf_tree_has_no_mismatch() {
    let tree = leaf(b"solo");
    assert_eq!(tree.find_mismatch(&mut Vec::new()), None);
}

#[test]
fn deep_consistent_tree_no_mismatch() {
    // 3-level tree: root -> [A, B], A -> [leaf, leaf], B -> [leaf, leaf]
    let a = consistent_internal(vec![leaf(b"a1"), leaf(b"a2")]);
    let b = consistent_internal(vec![leaf(b"b1"), leaf(b"b2")]);
    let root = consistent_internal(vec![a, b]);
    assert_eq!(root.find_mismatch(&mut Vec::new()), None);
}

#[test]
fn tampered_root_hash_detected_at_root() {
    let children = vec![leaf(b"x"), leaf(b"y")];
    let tree = Node::Internal {
        hash: [0xAB; 32],
        children,
    };
    // Children are consistent, so the walk descends, finds nothing, and
    // pins the mismatch to the root level (empty path).
    assert_eq!(tree.find_mismatch(&mut Vec::new()), Some(Vec::new()));
}

#[test]
fn tampered_leaf_data_detected_at_depth() {
    let good_left = consistent_internal(vec![leaf(b"l1"), leaf(b"l2")]);
    // Right child has a wrong stored hash
    let bad_right = Node::Internal {
        hash: [0xFF; 32],
        children: vec![leaf(b"r1"), leaf(b"r2")],
    };
    let root = Node::Internal {
        hash: [0x42; 32],
        children: vec![good_left, bad_right],
    };
    let path = root.find_mismatch(&mut Vec::new()).unwrap();
    assert_eq!(path, vec![1]);
}

#[test]
fn deeply_nested_tamper_pinpointed() {
    // root -> [A(consistent), B(tampered)]
    // B -> [C(consistent), D(tampered)]
    // D -> [leaf, leaf] with wrong hash
    let a = consistent_internal(vec![leaf(b"a1"), leaf(b"a2")]);
    let c = consistent_internal(vec![leaf(b"c1"), leaf(b"c2")]);
    let d = Node::Internal {
        hash: [0x01; 32],
        children: vec![leaf(b"d1"), leaf(b"d2")],
    };
    let b = Node::Internal {
        hash: [0x02; 32],
        children: vec![c, d],
    };
    let root = Node::Internal {
        hash: [0x03; 32],
        children: vec![a, b],
    };
    let path = root.find_mismatch(&mut Vec::new()).unwrap();
    assert_eq!(path, vec![1, 1]);
}

#[test]
fn many_children_consistent_no_mismatch() {
    let leaves: Vec<Node> = (0..10).map(|i| leaf(&[i])).collect();
    let tree = consistent_internal(leaves);
    assert_eq!(tree.find_mismatch(&mut Vec::new()), None);
}

#[test]
fn many_children_one_tampered_pinpointed() {
    let mut children: Vec<Node> = (0..8).map(|i| leaf(&[i])).collect();
    children.insert(
        4,
        Node::Internal {
            hash: [0xEE; 32],
            children: vec![leaf(b"tampered")],
        },
    );
    let root = Node::Internal {
        hash: [0xDD; 32],
        children,
    };
    let path = root.find_mismatch(&mut Vec::new()).unwrap();
    assert_eq!(path, vec![4]);
}

#[test]
fn empty_data_leaf_hash() {
    let empty = leaf(b"");
    let expected: [u8; 32] = Sha256::digest(b"").into();
    assert_eq!(empty.get_hash(), expected);
}

#[test]
fn identical_leaves_produce_identical_hashes() {
    assert_eq!(leaf(b"dup").get_hash(), leaf(b"dup").get_hash());
}

// ─── CLI pack/verify round-trip tests ─────────────────────────────────

fn cargo_bin(name: &str) -> PathBuf {
    // CI runs `cargo test --release`, so binaries live under target/release
    let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    path.push("target");
    path.push("release");
    path.push(name);
    path
}

struct TempDir {
    path: PathBuf,
}

impl TempDir {
    fn new(prefix: &str) -> Self {
        let mut path = std::env::temp_dir();
        path.push(format!("evk_test_{}_{}", prefix, std::process::id()));
        fs::create_dir_all(&path).unwrap();
        TempDir { path }
    }

    fn join(&self, name: &str) -> PathBuf {
        self.path.join(name)
    }
}

impl Drop for TempDir {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.path);
    }
}

fn write_file(path: &PathBuf, content: &[u8]) {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).unwrap();
    }
    fs::write(path, content).unwrap();
}

fn run_evk(args: &[&str]) -> (bool, String, String) {
    let output = std::process::Command::new(cargo_bin("evk"))
        .args(args)
        .output()
        .expect("failed to run evk binary");
    (
        output.status.success(),
        String::from_utf8_lossy(&output.stdout).to_string(),
        String::from_utf8_lossy(&output.stderr).to_string(),
    )
}

fn create_bundle(tmp: &TempDir) -> PathBuf {
    let job = tmp.join("job.txt");
    let snapshot = tmp.join("snapshot.bin");
    let input = tmp.join("input.dat");
    let output = tmp.join("bundle.evkp");

    write_file(&job, b"job content line 1\njob content line 2");
    write_file(&snapshot, &[0xDE, 0xAD, 0xBE, 0xEF]);
    write_file(&input, b"input payload data");

    let (ok, stdout, stderr) = run_evk(&[
        "pack",
        "--job",
        job.to_str().unwrap(),
        "--snapshot",
        snapshot.to_str().unwrap(),
        "--input",
        input.to_str().unwrap(),
        "--output",
        output.to_str().unwrap(),
    ]);
    assert!(ok, "pack failed: {} {}", stdout, stderr);
    assert!(output.exists(), "bundle file was not created");
    output
}

fn open_zip(path: &PathBuf) -> ZipArchive<std::fs::File> {
    let file = fs::File::open(path).unwrap();
    ZipArchive::new(file).unwrap()
}

#[test]
fn pack_creates_valid_zip_with_manifest() {
    let tmp = TempDir::new("pack_manifest");
    let bundle = create_bundle(&tmp);
    let zip = open_zip(&bundle);

    // Must contain manifest.json and the three evidence files
    let names: Vec<String> = zip.file_names().map(|n| n.to_string()).collect();
    assert!(names.contains(&"manifest.json".to_string()));
    assert!(names.contains(&"job.txt".to_string()));
    assert!(names.contains(&"snapshot.bin".to_string()));
    assert!(names.contains(&"input.dat".to_string()));
    assert_eq!(names.len(), 4);
}

#[test]
fn pack_manifest_has_correct_structure() {
    let tmp = TempDir::new("pack_structure");
    let bundle = create_bundle(&tmp);
    let mut zip = open_zip(&bundle);

    let mut manifest_bytes = Vec::new();
    zip.by_name("manifest.json")
        .unwrap()
        .read_to_end(&mut manifest_bytes)
        .unwrap();
    let manifest: serde_json::Value = serde_json::from_slice(&manifest_bytes).unwrap();

    assert_eq!(manifest["version"], "1.0");
    assert!(manifest["created"].is_string());
    assert!(manifest["manifest_hash"].is_string());
    assert!(manifest["files"].is_array());
    assert!(manifest["order"].is_array());

    let files = manifest["files"].as_array().unwrap();
    assert_eq!(files.len(), 3);
    for entry in files {
        assert!(entry["path"].is_string());
        assert!(entry["hash"].as_str().unwrap().starts_with("sha256:"));
    }

    let order = manifest["order"].as_array().unwrap();
    assert_eq!(order.len(), 3);
}

#[test]
fn pack_manifest_hash_is_correct() {
    let tmp = TempDir::new("pack_manifest_hash");
    let bundle = create_bundle(&tmp);
    let mut zip = open_zip(&bundle);

    let mut manifest_bytes = Vec::new();
    zip.by_name("manifest.json")
        .unwrap()
        .read_to_end(&mut manifest_bytes)
        .unwrap();
    let manifest: serde_json::Value = serde_json::from_slice(&manifest_bytes).unwrap();

    let mut manifest_no_hash = manifest.clone();
    manifest_no_hash
        .as_object_mut()
        .unwrap()
        .remove("manifest_hash");
    let canonical = serde_json::to_string(&manifest_no_hash).unwrap();
    let computed = format!("sha256:{:x}", Sha256::digest(canonical.as_bytes()));
    assert_eq!(manifest["manifest_hash"].as_str().unwrap(), computed);
}

#[test]
fn pack_file_hashes_match_zip_contents() {
    let tmp = TempDir::new("pack_file_hashes");
    let bundle = create_bundle(&tmp);
    let mut zip = open_zip(&bundle);

    let mut manifest_bytes = Vec::new();
    zip.by_name("manifest.json")
        .unwrap()
        .read_to_end(&mut manifest_bytes)
        .unwrap();
    let manifest: serde_json::Value = serde_json::from_slice(&manifest_bytes).unwrap();

    for entry in manifest["files"].as_array().unwrap() {
        let path = entry["path"].as_str().unwrap();
        let expected = entry["hash"].as_str().unwrap();

        let mut buf = Vec::new();
        zip.by_name(path).unwrap().read_to_end(&mut buf).unwrap();
        let actual = format!("sha256:{:x}", Sha256::digest(&buf));
        assert_eq!(actual, expected, "hash mismatch for {}", path);
    }
}

#[test]
fn verify_clean_bundle_succeeds() {
    let tmp = TempDir::new("verify_clean");
    let bundle = create_bundle(&tmp);

    let (ok, stdout, _stderr) = run_evk(&["verify", "--bundle", bundle.to_str().unwrap()]);
    assert!(ok, "verify should succeed for clean bundle: {}", stdout);
    assert!(stdout.contains("VALID"));
}

#[test]
fn verify_with_cert_emits_cert_line() {
    let tmp = TempDir::new("verify_cert");
    let bundle = create_bundle(&tmp);

    let (ok, stdout, _stderr) =
        run_evk(&["verify", "--bundle", bundle.to_str().unwrap(), "--cert"]);
    assert!(ok);
    assert!(stdout.contains("VALID"));
    assert!(stdout.contains("CERT:"));
    assert!(stdout.contains("files verified"));
}

#[test]
fn verify_nonexistent_bundle_fails() {
    let (ok, _stdout, stderr) = run_evk(&["verify", "--bundle", "/nonexistent/path/bundle.evkp"]);
    assert!(!ok);
    assert!(stderr.contains("Failed to open bundle") || stderr.contains("not a valid"));
}

#[test]
fn pack_nonexistent_input_fails() {
    let tmp = TempDir::new("pack_missing");
    let output = tmp.join("out.evkp");

    let (ok, _stdout, stderr) = run_evk(&[
        "pack",
        "--job",
        "/nonexistent/job.txt",
        "--snapshot",
        "/nonexistent/snap.bin",
        "--input",
        "/nonexistent/input.dat",
        "--output",
        output.to_str().unwrap(),
    ]);
    assert!(!ok);
    assert!(stderr.contains("Failed to read evidence file") || stderr.contains("No such file"));
}

#[test]
fn pack_is_deterministic_with_source_date_epoch() {
    let tmp = TempDir::new("pack_deterministic");

    let job = tmp.join("job.txt");
    let snapshot = tmp.join("snapshot.bin");
    let input = tmp.join("input.dat");
    write_file(&job, b"deterministic content");
    write_file(&snapshot, b"snap");
    write_file(&input, b"input");

    let out1 = tmp.join("bundle1.evkp");
    let out2 = tmp.join("bundle2.evkp");

    let run = |output: &PathBuf| {
        std::process::Command::new(cargo_bin("evk"))
            .args([
                "pack",
                "--job",
                job.to_str().unwrap(),
                "--snapshot",
                snapshot.to_str().unwrap(),
                "--input",
                input.to_str().unwrap(),
                "--output",
                output.to_str().unwrap(),
            ])
            .env("SOURCE_DATE_EPOCH", "1700000000")
            .output()
            .unwrap();
    };

    run(&out1);
    run(&out2);

    let bytes1 = fs::read(&out1).unwrap();
    let bytes2 = fs::read(&out2).unwrap();
    assert_eq!(
        bytes1, bytes2,
        "pack output should be byte-identical with fixed SOURCE_DATE_EPOCH"
    );
}

#[test]
fn pack_created_uses_source_date_epoch() {
    let tmp = TempDir::new("pack_sde");

    let job = tmp.join("job.txt");
    let snapshot = tmp.join("snapshot.bin");
    let input = tmp.join("input.dat");
    let output = tmp.join("bundle.evkp");
    write_file(&job, b"j");
    write_file(&snapshot, b"s");
    write_file(&input, b"i");

    std::process::Command::new(cargo_bin("evk"))
        .args([
            "pack",
            "--job",
            job.to_str().unwrap(),
            "--snapshot",
            snapshot.to_str().unwrap(),
            "--input",
            input.to_str().unwrap(),
            "--output",
            output.to_str().unwrap(),
        ])
        .env("SOURCE_DATE_EPOCH", "1700000000")
        .output()
        .unwrap();

    let mut zip = open_zip(&output);
    let mut manifest_bytes = Vec::new();
    zip.by_name("manifest.json")
        .unwrap()
        .read_to_end(&mut manifest_bytes)
        .unwrap();
    let manifest: serde_json::Value = serde_json::from_slice(&manifest_bytes).unwrap();

    // 1700000000 seconds since epoch = 2023-11-14T22:13:20+00:00
    assert_eq!(
        manifest["created"].as_str().unwrap(),
        "2023-11-14T22:13:20+00:00"
    );
}

#[test]
fn pack_default_created_is_epoch() {
    let tmp = TempDir::new("pack_default_created");

    let job = tmp.join("job.txt");
    let snapshot = tmp.join("snapshot.bin");
    let input = tmp.join("input.dat");
    let output = tmp.join("bundle.evkp");
    write_file(&job, b"j");
    write_file(&snapshot, b"s");
    write_file(&input, b"i");

    // Ensure SOURCE_DATE_EPOCH is not set
    std::process::Command::new(cargo_bin("evk"))
        .args([
            "pack",
            "--job",
            job.to_str().unwrap(),
            "--snapshot",
            snapshot.to_str().unwrap(),
            "--input",
            input.to_str().unwrap(),
            "--output",
            output.to_str().unwrap(),
        ])
        .env_remove("SOURCE_DATE_EPOCH")
        .output()
        .unwrap();

    let mut zip = open_zip(&output);
    let mut manifest_bytes = Vec::new();
    zip.by_name("manifest.json")
        .unwrap()
        .read_to_end(&mut manifest_bytes)
        .unwrap();
    let manifest: serde_json::Value = serde_json::from_slice(&manifest_bytes).unwrap();

    assert_eq!(
        manifest["created"].as_str().unwrap(),
        "1970-01-01T00:00:00+00:00"
    );
}

#[test]
fn verify_tampered_manifest_hash_fails() {
    let tmp = TempDir::new("verify_tampered_manifest");
    let bundle = create_bundle(&tmp);

    // Rebuild the zip with a corrupted manifest_hash
    let mut zip = open_zip(&bundle);
    let mut entries: Vec<(String, Vec<u8>)> = Vec::new();
    for i in 0..zip.len() {
        let mut entry = zip.by_index(i).unwrap();
        let name = entry.name().to_string();
        let mut buf = Vec::new();
        entry.read_to_end(&mut buf).unwrap();
        if name == "manifest.json" {
            let mut manifest: serde_json::Value = serde_json::from_slice(&buf).unwrap();
            manifest["manifest_hash"] = serde_json::json!("sha256:deadbeef");
            buf = serde_json::to_vec_pretty(&manifest).unwrap();
        }
        entries.push((name, buf));
    }

    let tampered = tmp.join("tampered.evkp");
    let file = fs::File::create(&tampered).unwrap();
    let mut zw = zip::ZipWriter::new(file);
    let opts = zip::write::FileOptions::default();
    for (name, data) in &entries {
        zw.start_file(name, opts).unwrap();
        std::io::Write::write_all(&mut zw, data).unwrap();
    }
    zw.finish().unwrap();

    let (ok, _stdout, stderr) = run_evk(&["verify", "--bundle", tampered.to_str().unwrap()]);
    assert!(!ok, "verify should fail for tampered manifest_hash");
    assert!(stderr.contains("manifest_hash mismatch") || stderr.contains("INVALID"));
}

#[test]
fn verify_tampered_file_content_fails() {
    let tmp = TempDir::new("verify_tampered_content");
    let bundle = create_bundle(&tmp);

    // Rebuild the zip with corrupted file content
    let mut zip = open_zip(&bundle);
    let mut entries: Vec<(String, Vec<u8>)> = Vec::new();
    for i in 0..zip.len() {
        let mut entry = zip.by_index(i).unwrap();
        let name = entry.name().to_string();
        let mut buf = Vec::new();
        entry.read_to_end(&mut buf).unwrap();
        if name == "job.txt" {
            buf[0] ^= 0xFF; // flip first byte
        }
        entries.push((name, buf));
    }

    let tampered = tmp.join("tampered.evkp");
    let file = fs::File::create(&tampered).unwrap();
    let mut zw = zip::ZipWriter::new(file);
    let opts = zip::write::FileOptions::default();
    for (name, data) in &entries {
        zw.start_file(name, opts).unwrap();
        std::io::Write::write_all(&mut zw, data).unwrap();
    }
    zw.finish().unwrap();

    let (ok, _stdout, stderr) = run_evk(&["verify", "--bundle", tampered.to_str().unwrap()]);
    assert!(!ok, "verify should fail for tampered file content");
    assert!(stderr.contains("hash mismatch") || stderr.contains("INVALID"));
}

#[test]
fn verify_missing_manifest_fails() {
    let tmp = TempDir::new("verify_no_manifest");

    // Create a zip with just one file, no manifest
    let bundle = tmp.join("no_manifest.evkp");
    let file = fs::File::create(&bundle).unwrap();
    let mut zw = zip::ZipWriter::new(file);
    let opts = zip::write::FileOptions::default();
    zw.start_file("job.txt", opts).unwrap();
    std::io::Write::write_all(&mut zw, b"no manifest here").unwrap();
    zw.finish().unwrap();

    let (ok, _stdout, stderr) = run_evk(&["verify", "--bundle", bundle.to_str().unwrap()]);
    assert!(!ok);
    assert!(stderr.contains("manifest") || stderr.contains("missing"));
}

#[test]
fn pack_then_verify_round_trip_multiple_files() {
    let tmp = TempDir::new("round_trip_multi");

    // Create files of varying sizes
    let job = tmp.join("job.txt");
    let snapshot = tmp.join("snapshot.bin");
    let input = tmp.join("input.dat");
    let output = tmp.join("bundle.evkp");

    write_file(&job, b"job data with multiple lines\nline 2\nline 3");
    write_file(&snapshot, &[0xAA; 100]);
    write_file(&input, &[]); // empty input file

    let (ok, stdout, stderr) = run_evk(&[
        "pack",
        "--job",
        job.to_str().unwrap(),
        "--snapshot",
        snapshot.to_str().unwrap(),
        "--input",
        input.to_str().unwrap(),
        "--output",
        output.to_str().unwrap(),
    ]);
    assert!(ok, "pack failed: {} {}", stdout, stderr);

    let (ok, stdout, _stderr) = run_evk(&["verify", "--bundle", output.to_str().unwrap()]);
    assert!(ok, "verify failed: {}", stdout);
    assert!(stdout.contains("VALID"));
    assert!(stdout.contains("\"files_verified\": 3"));
}
