use sha2::{Digest, Sha256};

type Hash = [u8; 32];

pub enum Node {
    Leaf { data: Vec<u8> }, // Changed from hash to data for real verification
    Internal { hash: Hash, children: Vec<Node> },
}

impl Node {
    // Helper to get hash of a node
    pub fn get_hash(&self) -> Hash {
        match self {
            Node::Leaf { data } => {
                let mut hasher = Sha256::new();
                hasher.update(data);
                hasher.finalize().into()
            }
            Node::Internal { hash, .. } => *hash,
        }
    }

    pub fn find_mismatch(&self, path: &mut Vec<usize>) -> Option<Vec<usize>> {
        match self {
            Node::Leaf { .. } => {
                // A leaf carries its own data; its hash is derived, never stored,
                // so a leaf on its own can never be internally inconsistent.
                None
            }
            Node::Internal { hash, children } => {
                let mut hasher = Sha256::new();
                for child in children {
                    hasher.update(child.get_hash());
                }
                let computed: Hash = hasher.finalize().into();

                if computed == *hash {
                    return None;
                }

                for (idx, child) in children.iter().enumerate() {
                    path.push(idx);
                    if let Some(bad_path) = child.find_mismatch(path) {
                        return Some(bad_path);
                    }
                    path.pop();
                }
                Some(path.clone())
            }
        }
    }
}

/// Compute the hash an [`Node::Internal`] should carry for the given children.
pub fn internal_hash(children: &[Node]) -> Hash {
    let mut hasher = Sha256::new();
    for child in children {
        hasher.update(child.get_hash());
    }
    hasher.finalize().into()
}

#[cfg(test)]
mod tests {
    use super::*;

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
    fn leaf_hash_is_sha256_of_data() {
        let expected: Hash = Sha256::digest(b"abc").into();
        assert_eq!(leaf(b"abc").get_hash(), expected);
    }

    #[test]
    fn consistent_tree_has_no_mismatch() {
        let tree = consistent_internal(vec![leaf(b"a"), leaf(b"b")]);
        assert_eq!(tree.find_mismatch(&mut Vec::new()), None);
    }

    #[test]
    fn tampered_internal_hash_is_detected() {
        let tree = Node::Internal {
            hash: [0u8; 32],
            children: vec![leaf(b"a"), leaf(b"b")],
        };
        assert_eq!(tree.find_mismatch(&mut Vec::new()), Some(Vec::new()));
    }

    #[test]
    fn nested_tampered_child_path_is_reported() {
        let good_child = consistent_internal(vec![leaf(b"a"), leaf(b"b")]);
        let bad_child = Node::Internal {
            hash: [0u8; 32],
            children: vec![leaf(b"c")],
        };
        // The root's stored hash is also wrong, so the walk descends and pins
        // the inconsistency to child index 1.
        let root = Node::Internal {
            hash: [9u8; 32],
            children: vec![good_child, bad_child],
        };
        assert_eq!(root.find_mismatch(&mut Vec::new()), Some(vec![1]));
    }
}
