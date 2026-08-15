"""Command-line interface for encryption, decryption, and core analysis."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

from .analysis.metrics import adjacent_correlation, information_entropy
from .cipher import decrypt_array, encrypt_array
from .config import CipherConfig
from .io import load_image, save_image
from .key_schedule import KeyMaterial


def _load_config(path: str | None) -> CipherConfig:
    return CipherConfig.load(path) if path else CipherConfig()


def cmd_encrypt(args: argparse.Namespace) -> int:
    config = _load_config(args.config)
    image, raw = load_image(args.input, force_rgb=not args.grayscale)
    cipher, key = encrypt_array(image, config, file_bytes=raw)
    save_image(args.output, cipher)
    key.save(args.key_output)
    print(f"encrypted: {args.output}")
    print(f"key material: {args.key_output}")
    return 0


def cmd_decrypt(args: argparse.Namespace) -> int:
    key = KeyMaterial.load(args.key)
    config = CipherConfig.load(args.config) if args.config else CipherConfig.from_dict(key.config)
    cipher, _ = load_image(args.input, force_rgb=not args.grayscale)
    plain = decrypt_array(cipher, key, config)
    save_image(args.output, plain)
    print(f"decrypted: {args.output}")
    return 0


def cmd_metrics(args: argparse.Namespace) -> int:
    image, _ = load_image(args.input, force_rgb=not args.grayscale)
    entropy = information_entropy(image)
    corr = adjacent_correlation(image)
    payload = {
        "entropy": entropy.tolist(),
        "correlation": {k: v.tolist() for k, v in corr.items()},
    }
    text = json.dumps(payload, indent=2)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="threedsff", description="Paper-derived 3DSFF image encryption reproduction")
    sub = parser.add_subparsers(dest="command", required=True)

    enc = sub.add_parser("encrypt", help="encrypt an image and write key material")
    enc.add_argument("--input", required=True)
    enc.add_argument("--output", required=True)
    enc.add_argument("--key-output", required=True)
    enc.add_argument("--config")
    enc.add_argument("--grayscale", action="store_true", help="preserve grayscale instead of converting to RGB")
    enc.set_defaults(func=cmd_encrypt)

    dec = sub.add_parser("decrypt", help="decrypt using stored key material")
    dec.add_argument("--input", required=True)
    dec.add_argument("--key", required=True)
    dec.add_argument("--output", required=True)
    dec.add_argument("--config")
    dec.add_argument("--grayscale", action="store_true")
    dec.set_defaults(func=cmd_decrypt)

    met = sub.add_parser("metrics", help="compute entropy and adjacent-pixel correlation")
    met.add_argument("--input", required=True)
    met.add_argument("--output")
    met.add_argument("--grayscale", action="store_true")
    met.set_defaults(func=cmd_metrics)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
