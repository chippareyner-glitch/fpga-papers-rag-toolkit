import os
import sys
import subprocess
import time
import urllib.request
import re
from pathlib import Path

# Force UTF-8 stdout
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DOCUMENTS_DIR = Path(r"D:\Vivado_RAG\documents")
PAPERS_DIR = DOCUMENTS_DIR / "papers"
PAPERS_DIR.mkdir(parents=True, exist_ok=True)

# 1. ArXiv Papers (URL without .pdf extension for canonical arXiv redirect)
ARXIV_PAPERS = [
    ("Paper_2312.15159_Understanding_FPGA_Spatial_LLM.pdf", "https://arxiv.org/pdf/2312.15159"),
    ("Paper_2410.07546_The_BRAM_is_the_Limit.pdf", "https://arxiv.org/pdf/2410.07546"),
    ("Paper_2401.03868_FlightLLM_FPGA24.pdf", "https://arxiv.org/pdf/2401.03868"),
    ("Paper_2407.21325_EdgeLLM.pdf", "https://arxiv.org/pdf/2407.21325"),
    ("Paper_2502.10659_Pushing_Memory_Bandwidth_Embedded_FPGA.pdf", "https://arxiv.org/pdf/2502.10659"),
    ("Paper_2507.03308_Hummingbird_GQA_DDR4.pdf", "https://arxiv.org/pdf/2507.03308"),
    ("Paper_2505.03745_AccLLM_Roofline_Analysis.pdf", "https://arxiv.org/pdf/2505.03745"),
    ("Paper_2504.17376_On_Device_Qwen2.5_on_FPGA.pdf", "https://arxiv.org/pdf/2504.17376"),
    ("Paper_2602.06063_Mapping_Gemma3_Edge_Dataflow.pdf", "https://arxiv.org/pdf/2602.06063"),
    ("Paper_2603.14785_SkipOPU_FlashAttention_FPGA.pdf", "https://arxiv.org/pdf/2603.14785"),
    ("Paper_1908.01261_IO_Cache_Coherency_SoC_FPGA.pdf", "https://arxiv.org/pdf/1908.01261"),
    ("Paper_2005.04324_Benchmarking_HBM_DRAM_FPGAs.pdf", "https://arxiv.org/pdf/2005.04324"),
    ("Paper_2104.07776_Demystifying_Memory_Access_Patterns_FPGA.pdf", "https://arxiv.org/pdf/2104.07776"),
]

# 2. Official AMD / Xilinx Architectural Guides
AMD_DOCS = [
    ("ug1037-vivado-axi-reference-guide.pdf", "https://www.xilinx.com/content/dam/xilinx/support/documents/ip_documentation/axi_ref_guide/latest/ug1037-vivado-axi-reference-guide.pdf"),
    ("pg058-blk-mem-gen.pdf", "https://www.xilinx.com/content/dam/xilinx/support/documents/ip_documentation/blk_mem_gen/v8_4/pg058-blk-mem-gen.pdf"),
    ("pg059-axi-interconnect.pdf", "https://www.xilinx.com/content/dam/xilinx/support/documents/ip_documentation/axi_interconnect/v2_1/pg059-axi-interconnect.pdf"),
    ("pg037-axi-perf-mon.pdf", "https://www.xilinx.com/content/dam/xilinx/support/documents/ip_documentation/axi_perf_mon/v5_0/pg037-axi-perf-mon.pdf"),
]

# 3. ZipCPU Blog Articles
ZIPCPU_ARTICLES = [
    ("ZipCPU_AXI_Address_Limits_and_Burst.pdf", "https://zipcpu.com/blog/2020/06/16/axiaddr-limits.html"),
    ("ZipCPU_Measuring_AXI_Latency_and_Throughput.pdf", "https://zipcpu.com/blog/2021/08/14/axiperf.html"),
]

def is_valid_pdf(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 10240:
        return False
    try:
        with open(path, "rb") as f:
            return f.read(5) == b"%PDF-"
    except Exception:
        return False

def download_with_curl(filename: str, url: str) -> bool:
    target = PAPERS_DIR / filename
    if is_valid_pdf(target):
        size_kb = target.stat().st_size // 1024
        print(f"[SKIP] {filename} already exists ({size_kb} KB)")
        return True

    temp_target = PAPERS_DIR / f"{filename}.part"
    print(f"[DOWNLOADING] {filename} from {url}...")
    
    cmd = [
        "curl.exe", "-L", "-s", "--connect-timeout", "15", "--max-time", "60",
        "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "-o", str(temp_target),
        url
    ]
    for attempt in range(1, 4):
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            if res.returncode == 0 and is_valid_pdf(temp_target):
                if target.exists():
                    target.unlink()
                temp_target.rename(target)
                size_kb = target.stat().st_size // 1024
                print(f"[SUCCESS] {filename} saved ({size_kb} KB)")
                return True
            else:
                print(f"  Attempt {attempt} failed (code {res.returncode}). Retrying in 2s...")
                time.sleep(2)
        except Exception as e:
            print(f"  Attempt {attempt} exception: {e}")
            time.sleep(2)

    if temp_target.exists():
        temp_target.unlink()
    print(f"[FAILED] Could not download {filename}")
    return False

def convert_html_to_pdf(filename: str, url: str) -> bool:
    target = PAPERS_DIR / filename
    if is_valid_pdf(target):
        print(f"[SKIP] {filename} already exists")
        return True

    print(f"[FETCHING ARTICLE] {filename} from {url}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')

        # Extract text content from HTML
        # Strip script and style tags
        html_clean = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.DOTALL)
        # Convert paragraphs / breaks to newlines
        html_clean = re.sub(r'<br\s*/?>', '\n', html_clean)
        html_clean = re.sub(r'</p>', '\n\n', html_clean)
        html_clean = re.sub(r'</(h[1-6]|div|li|tr)>', '\n', html_clean)
        # Strip all other HTML tags
        text = re.sub(r'<[^>]+>', '', html_clean)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        clean_text = "\n".join(lines)

        import pymupdf
        doc = pymupdf.open()
        
        # Paginate text into PDF pages (approx 40 lines per page)
        lines = clean_text.split('\n')
        chunk_size = 40
        for i in range(0, len(lines), chunk_size):
            page_text = "\n".join(lines[i:i+chunk_size])
            page = doc.new_page()
            # Rect margin: left 50, top 50, right 550, bottom 790
            rect = pymupdf.Rect(50, 50, 550, 790)
            page.insert_textbox(rect, page_text, fontsize=10, fontname="helv")

        doc.save(str(target))
        doc.close()
        size_kb = target.stat().st_size // 1024
        print(f"[SUCCESS] Converted and saved {filename} ({size_kb} KB)")
        return True
    except Exception as e:
        print(f"[FAILED] Error converting {url} to PDF: {e}")
        return False

def main():
    print("=" * 60)
    print("Starting download of pure RTL FPGA & LLM research papers...")
    print(f"Target directory: {PAPERS_DIR}")
    print("=" * 60)

    # 1. Download arXiv papers
    for filename, url in ARXIV_PAPERS:
        download_with_curl(filename, url)
        time.sleep(1)

    # 2. Download AMD IP Reference Guides
    for filename, url in AMD_DOCS:
        download_with_curl(filename, url)
        time.sleep(1)

    # 3. Convert ZipCPU blog articles
    for filename, url in ZIPCPU_ARTICLES:
        convert_html_to_pdf(filename, url)

    print("\n" + "=" * 60)
    print("All paper downloads & article conversions finished.")
    print("=" * 60)

if __name__ == "__main__":
    main()
