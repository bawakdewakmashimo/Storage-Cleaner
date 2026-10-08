#!/usr/bin/env python3
"""
Storage Audit & Optimization Utility
Script: storage_audit.py
Runtime: Python 3 (Standard libraries only: os, hashlib, sys, pathlib)
Zero external dependencies (pip install NOT required)
"""

import os
import sys
import hashlib
from pathlib import Path

# Threshold 2 MB = 2 * 1024 * 1024 bytes (2.048 KB)
GIANT_FILE_THRESHOLD_BYTES = 2 * 1024 * 1024

def format_bytes(b):
    if b == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    val = float(b)
    while val >= 1024 and i < len(units) - 1:
        val /= 1024.0
        i += 1
    return f"{val:.2f} {units[i]}"

def compute_sha256(filepath):
    h = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None

def resolve_target_dir(custom_path=None):
    if custom_path and os.path.isdir(custom_path):
        return os.path.abspath(custom_path)
    
    candidates = [
        os.path.abspath("Downloads_Lab"),
        os.path.join(str(Path.home()), "Downloads", "Downloads_Lab"),
        os.path.join(os.path.dirname(__file__), "Downloads_Lab"),
        os.path.abspath(os.path.join("..", "Downloads_Lab")),
        os.path.join(str(Path.home()), "Downloads_Lab")
    ]
    for c in candidates:
        if os.path.isdir(c):
            return c
    return None

def scan_files(directory):
    files = []
    for root, _, filenames in os.walk(directory):
        for name in filenames:
            full_path = os.path.join(root, name)
            try:
                st = os.stat(full_path)
                is_tmp = name.lower().endswith('.tmp') or name.startswith('~')
                files.append({
                    'name': name,
                    'path': full_path,
                    'size': st.st_size,
                    'mtime': st.st_mtime,
                    'is_tmp': is_tmp
                })
            except Exception:
                pass
    return files

def main():
    custom_arg = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-') else None
    target_path = resolve_target_dir(custom_arg)

    if not target_path:
        print("❌ Error: Folder 'Downloads_Lab' tidak ditemukan!")
        sys.exit(1)

    print("╭" + "─" * 78 + "╮")
    print("│ STORAGE AUDIT & OPTIMIZATION UTILITY [Python Engine]                       │")
    print(f"│ Target: {target_path[:68]:<68} │")
    print("╰" + "─" * 78 + "╯\n")

    print("⏳ Memindai file secara rekursif...")
    files = scan_files(target_path)
    print(f"✔ Berhasil memindai {len(files)} file.\n")

    print("🔒 Menghitung SHA-256 hash setiap file...")
    giant_files = []
    tmp_files = []
    hash_map = {}
    total_bytes = 0

    for f in files:
        total_bytes += f['size']
        if f['is_tmp']:
            tmp_files.append(f)
        if f['size'] >= GIANT_FILE_THRESHOLD_BYTES:
            giant_files.append(f)

        f_hash = compute_sha256(f['path'])
        if f_hash:
            f['hash'] = f_hash
            hash_map.setdefault(f_hash, []).append(f)

    duplicate_groups = []
    reclaimable_bytes = 0
    redundant_count = 0

    for h, group in hash_map.items():
        if len(group) > 1:
            group.sort(key=lambda x: (
                1 if any(k in x['name'].lower() for k in ['copy', 'salinan', 'backup', '_v']) else 0,
                x['mtime']
            ))
            orig = group[0]
            dups = group[1:]
            group_saving = sum(d['size'] for d in dups)
            reclaimable_bytes += group_saving
            redundant_count += len(dups)
            duplicate_groups.append({
                'hash': h,
                'original': orig,
                'duplicates': dups,
                'savings': group_saving
            })

    print("\n" + "=" * 80)
    print("📊 RINGKASAN AUDIT PENYIMPANAN")
    print("=" * 80)
    print(f"  • Total File Di-scan      : {len(files)} file")
    print(f"  • Total Ukuran Folder     : {format_bytes(total_bytes)}")
    print(f"  • File Raksasa (≥ 2 MB)   : {len(giant_files)} file")
    print(f"  • Kelompok Duplikat       : {len(duplicate_groups)} kelompok ({redundant_count} file salinan)")
    print(f"  • File Sampah (.tmp)      : {len(tmp_files)} file")
    print(f"  • ESTIMASI HEMAT RUANG    : {format_bytes(reclaimable_bytes)}")
    print("=" * 80 + "\n")

    print(f"📦 DAFTAR FILE RAKSASA (> 2 MB / 2.048 KB) [{len(giant_files)} File]")
    giant_files.sort(key=lambda x: x['size'], reverse=True)
    for idx, gf in enumerate(giant_files, 1):
        rel = os.path.relpath(gf['path'], target_path)
        print(f"   {idx:2d}. [{format_bytes(gf['size']):>10}] {gf['name']}")
        print(f"       Path: {rel}")
    print()

    print(f"🔄 DAFTAR KELOMPOK DUPLIKAT (SHA-256 Identik) [{len(duplicate_groups)} Kelompok]")
    duplicate_groups.sort(key=lambda x: x['savings'], reverse=True)
    for idx, grp in enumerate(duplicate_groups, 1):
        print(f"   Grup #{idx} (SHA-256: {grp['hash'][:12]}... | Potensi hemat: {format_bytes(grp['savings'])})")
        print(f"     ✔ [DIPERTAHANKAN] {grp['original']['name']}")
        for d in grp['duplicates']:
            print(f"     ✖ [SALINAN DUPLIKAT] {d['name']}")
        print()

    if tmp_files:
        print(f"🗑️ FILE SAMPAH (.tmp) [{len(tmp_files)} File]")
        for tf in tmp_files:
            print(f"   - {tf['name']} ({format_bytes(tf['size'])})")
        print()

    if not duplicate_groups and not tmp_files:
        print("✨ Folder bersih! Tidak ada duplikat yang perlu dihapus.")
        return

    if "--dry-run" in sys.argv:
        print("ℹ️ Mode dry-run: Tidak ada file yang dihapus.")
        return

    ans = input("Apakah kamu ingin menghapus file duplikat yang tidak terpakai? (Y/N): ").strip().lower()
    if ans in ['y', 'ya', 'yes']:
        deleted = 0
        freed = 0
        for grp in duplicate_groups:
            for d in grp['duplicates']:
                try:
                    if os.path.exists(d['path']):
                        os.remove(d['path'])
                        deleted += 1
                        freed += d['size']
                        print(f"  ✔ BERHASIL DIHAPUS: {d['name']} (+{format_bytes(d['size'])})")
                except Exception as e:
                    print(f"  ✘ GAGAL MENGHAPUS: {d['name']} ({e})")
        for tf in tmp_files:
            try:
                if os.path.exists(tf['path']):
                    os.remove(tf['path'])
                    deleted += 1
                    freed += tf['size']
                    print(f"  ✔ BERHASIL DIHAPUS (.tmp): {tf['name']}")
            except Exception:
                pass
        print(f"\n🎉 Selesai! {deleted} file dihapus. Ruang dihemat: {format_bytes(freed)}")
    else:
        print("\nOperasi dibatalkan. Tidak ada file yang dihapus.")

if __name__ == '__main__':
    main()
