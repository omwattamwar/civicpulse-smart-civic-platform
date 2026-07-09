"""
CivicPulse AI Model Evaluation Script
======================================
Tests OpenAI CLIP ViT-L/14 zero-shot civic issue detection across 12 severity-aware classes.
Generates an accuracy report with confusion matrix and per-class metrics.
"""

import os
import io
import json
import sys
import urllib.request
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import datetime
from PIL import Image
from collections import defaultdict

# ---------------------------------------------------------------------------
# Test Dataset – curated images with known ground truth
# Each entry: (URL, expected_class, expected_priority, description)
# ---------------------------------------------------------------------------
TEST_DATASET = [
    (
        "../sample_images/garbage1.png",
        "severe garbage", "high",
        "Garbage pile on sidewalk"
    ),
    (
        "../sample_images/garbage2.png",
        "severe garbage", "high",
        "Garbage pile on street"
    ),
    (
        "../sample_images/road1.jpg",
        "severe pothole", "high",
        "Severe potholes with standing water"
    ),
    (
        "../sample_images/road2.jpg",
        "severe pothole", "high",
        "Severely damaged / collapsed road"
    ),
    (
        "../sample_images/water_leakage_1.png",
        "severe water leak", "high",
        "Water pooling on street"
    ),
    (
        "../sample_images/water_leakage_2.png",
        "severe water leak", "high",
        "Water flooding on street"
    ),
]

# Priority mapping (synced with main.py severity-aware classes)
CLASS_PRIORITY = {
    "severe pothole": "high",
    "minor road crack": "low",
    "severe garbage": "high",
    "minor garbage": "low",
    "broken traffic light": "high",
    "abandoned car": "medium",
    "severe water leak": "high",
    "minor water leak": "low",
    "damaged street sign": "medium",
    "graffiti": "low",
    "fallen tree": "high",
    "none": "none"
}

PRIORITY_ORDER = {"high": 3, "medium": 2, "low": 1, "none": 0}


def download_image(url):
    """Download image from URL or load from local path and return PIL Image."""
    if url.startswith("http://") or url.startswith("https://"):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            image_data = resp.read()
        return Image.open(io.BytesIO(image_data)).convert('RGB')
    else:
        # Resolve local path relative to this script
        local_path = os.path.join(os.path.dirname(__file__), url)
        return Image.open(local_path).convert('RGB')


# Synced with main.py — 12 severity-aware classes (balanced prompts)
CLIP_CLASSES = [
    "a photo of a pothole or severely damaged road with broken pavement",
    "a photo of a road with minor surface cracks and small imperfections",
    "a photo of garbage and trash dumped or piled on a street or sidewalk",
    "a photo of a small amount of litter on the ground",
    "a photo of a broken or malfunctioning traffic light",
    "a photo of an abandoned or derelict car on a street",
    "a photo of water flooding or leaking onto a road or sidewalk",
    "a photo of a small water puddle on the ground",
    "a photo of a damaged or bent street sign",
    "a photo of graffiti spray painted on a wall",
    "a photo of a fallen tree blocking a road or path",
    "a clean street with no visible problems or damage"
]

CLIP_CLASS_TO_SHORT = {
    "a photo of a pothole or severely damaged road with broken pavement": "severe pothole",
    "a photo of a road with minor surface cracks and small imperfections": "minor road crack",
    "a photo of garbage and trash dumped or piled on a street or sidewalk": "severe garbage",
    "a photo of a small amount of litter on the ground": "minor garbage",
    "a photo of a broken or malfunctioning traffic light": "broken traffic light",
    "a photo of an abandoned or derelict car on a street": "abandoned car",
    "a photo of water flooding or leaking onto a road or sidewalk": "severe water leak",
    "a photo of a small water puddle on the ground": "minor water leak",
    "a photo of a damaged or bent street sign": "damaged street sign",
    "a photo of graffiti spray painted on a wall": "graffiti",
    "a photo of a fallen tree blocking a road or path": "fallen tree",
    "a clean street with no visible problems or damage": "none"
}

def run_inference(model_tuple, img):
    """Run CLIP inference and return (detected_class, priority, confidence, all_detections)."""
    model, preprocess, text_tokens = model_tuple
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    image = preprocess(img).unsqueeze(0).to(device)
    with torch.no_grad():
        logits_per_image, logits_per_text = model(image, text_tokens)
        probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]

    all_detections = []
    for c, p in zip(CLIP_CLASSES, probs):
        all_detections.append({"class": CLIP_CLASS_TO_SHORT[c], "confidence": round(float(p), 4)})
        
    best_idx = probs.argmax()
    best_sentence = CLIP_CLASSES[best_idx]
    best_prob = float(probs[best_idx])
    short_class = CLIP_CLASS_TO_SHORT[best_sentence]
    
    if short_class == "none" or best_prob < 0.1:
        detected_class = "none"
        detected_priority = "none"
        highest_confidence = 0.0
    else:
        detected_class = short_class
        detected_priority = CLASS_PRIORITY.get(short_class, "medium")
        highest_confidence = round(best_prob, 4)

    return detected_class, detected_priority, highest_confidence, all_detections


def compute_metrics(results):
    """Compute accuracy, per-class precision/recall, and confusion matrix."""

    # Priority-level metrics
    priority_labels = ["high", "medium", "low", "none"]
    confusion = {true: {pred: 0 for pred in priority_labels} for true in priority_labels}

    class_tp = defaultdict(int)
    class_fp = defaultdict(int)
    class_fn = defaultdict(int)

    total = len(results)
    priority_correct = 0
    class_correct = 0

    for r in results:
        true_priority = r["expected_priority"]
        pred_priority = r["predicted_priority"]
        true_class = r["expected_class"]
        pred_class = r["predicted_class"]

        # Confusion matrix (priority level)
        if true_priority in confusion and pred_priority in confusion[true_priority]:
            confusion[true_priority][pred_priority] += 1

        # Priority accuracy
        if true_priority == pred_priority:
            priority_correct += 1

        # Class accuracy
        if true_class == pred_class:
            class_correct += 1
            class_tp[true_class] += 1
        else:
            class_fn[true_class] += 1
            class_fp[pred_class] += 1

    # Per-class precision/recall
    all_classes = sorted(set(
        [r["expected_class"] for r in results] + [r["predicted_class"] for r in results]
    ))
    class_metrics = {}
    for cls in all_classes:
        tp = class_tp[cls]
        fp = class_fp[cls]
        fn = class_fn[cls]
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        class_metrics[cls] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "tp": tp, "fp": fp, "fn": fn
        }

    return {
        "total_samples": total,
        "priority_accuracy": round(priority_correct / total * 100, 2) if total else 0,
        "class_accuracy": round(class_correct / total * 100, 2) if total else 0,
        "priority_correct": priority_correct,
        "class_correct": class_correct,
        "confusion_matrix": confusion,
        "class_metrics": class_metrics,
    }


def generate_html_report(results, metrics, output_path):
    """Generate a professional HTML report."""

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    priority_labels = ["high", "medium", "low", "none"]

    # Build confusion matrix HTML
    cm = metrics["confusion_matrix"]
    cm_rows = ""
    for true_p in priority_labels:
        cells = ""
        for pred_p in priority_labels:
            val = cm[true_p][pred_p]
            bg = "#2ecc71" if true_p == pred_p and val > 0 else ("#e74c3c" if val > 0 else "#2d3748")
            cells += f'<td style="background:{bg};color:#fff;padding:12px;text-align:center;font-weight:bold;">{val}</td>'
        cm_rows += f'<tr><td style="padding:12px;font-weight:bold;text-transform:capitalize;background:#1a202c;color:#cbd5e0;">{true_p}</td>{cells}</tr>'

    # Build per-class metrics table
    class_rows = ""
    for cls, m in sorted(metrics["class_metrics"].items()):
        priority = CLASS_PRIORITY.get(cls, "none")
        priority_badge_color = {"high": "#e74c3c", "medium": "#f39c12", "low": "#3498db", "none": "#718096"}.get(priority, "#718096")
        class_rows += f'''<tr>
            <td style="padding:10px;font-weight:500;">{cls.title()}</td>
            <td style="padding:10px;"><span style="background:{priority_badge_color};color:#fff;padding:3px 10px;border-radius:12px;font-size:12px;text-transform:uppercase;">{priority}</span></td>
            <td style="padding:10px;text-align:center;">{m["precision"]*100:.1f}%</td>
            <td style="padding:10px;text-align:center;">{m["recall"]*100:.1f}%</td>
            <td style="padding:10px;text-align:center;">{m["f1"]*100:.1f}%</td>
            <td style="padding:10px;text-align:center;">{m["tp"]}</td>
            <td style="padding:10px;text-align:center;">{m["fp"]}</td>
            <td style="padding:10px;text-align:center;">{m["fn"]}</td>
        </tr>'''

    # Build individual results table
    result_rows = ""
    for i, r in enumerate(results, 1):
        status = "✅" if r["priority_match"] else "❌"
        class_status = "✅" if r["class_match"] else "❌"
        conf_color = "#2ecc71" if r["confidence"] >= 0.5 else ("#f39c12" if r["confidence"] >= 0.2 else "#e74c3c")
        result_rows += f'''<tr style="border-bottom:1px solid #2d3748;">
            <td style="padding:10px;">{i}</td>
            <td style="padding:10px;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="{r['description']}">{r['description']}</td>
            <td style="padding:10px;">{r['expected_class'].title()}</td>
            <td style="padding:10px;">{r['predicted_class'].title()}</td>
            <td style="padding:10px;text-align:center;">{class_status}</td>
            <td style="padding:10px;text-transform:capitalize;">{r['expected_priority']}</td>
            <td style="padding:10px;text-transform:capitalize;">{r['predicted_priority']}</td>
            <td style="padding:10px;text-align:center;">{status}</td>
            <td style="padding:10px;text-align:center;"><span style="color:{conf_color};font-weight:bold;">{r['confidence']*100:.1f}%</span></td>
        </tr>'''

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CivicPulse AI Model Evaluation Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: #e2e8f0;
            min-height: 100vh;
            padding: 40px 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 40px;
            background: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(168,85,247,0.2));
            border-radius: 20px;
            border: 1px solid rgba(99,102,241,0.3);
            backdrop-filter: blur(10px);
        }}
        .header h1 {{
            font-size: 2.5em;
            background: linear-gradient(135deg, #818cf8, #a78bfa, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        .header p {{ color: #94a3b8; font-size: 1.1em; }}
        .header .timestamp {{ color: #64748b; font-size: 0.9em; margin-top: 8px; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .stat-card {{
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(99,102,241,0.2);
            border-radius: 16px;
            padding: 24px;
            text-align: center;
            backdrop-filter: blur(10px);
            transition: transform 0.2s;
        }}
        .stat-card:hover {{ transform: translateY(-4px); }}
        .stat-card .value {{
            font-size: 2.8em;
            font-weight: 700;
            margin-bottom: 4px;
        }}
        .stat-card .label {{ color: #94a3b8; font-size: 0.95em; text-transform: uppercase; letter-spacing: 1px; }}
        .green {{ color: #2ecc71; }}
        .yellow {{ color: #f39c12; }}
        .blue {{ color: #3498db; }}
        .purple {{ color: #a78bfa; }}
        .section {{
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(99,102,241,0.15);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }}
        .section h2 {{
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #c084fc;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{
            background: #1a202c;
            color: #a78bfa;
            padding: 14px 10px;
            text-align: left;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        td {{ padding: 10px; border-bottom: 1px solid #2d3748; }}
        tr:hover {{ background: rgba(99,102,241,0.05); }}
        .model-info {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }}
        .model-info div {{
            padding: 12px 16px;
            background: rgba(15, 23, 42, 0.5);
            border-radius: 8px;
            border-left: 3px solid #6366f1;
        }}
        .model-info .label {{ color: #64748b; font-size: 0.85em; }}
        .model-info .value {{ color: #e2e8f0; font-weight: 600; margin-top: 4px; }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #475569;
            font-size: 0.85em;
            margin-top: 20px;
        }}
        @media (max-width: 768px) {{
            .model-info {{ grid-template-columns: 1fr; }}
            .stats-grid {{ grid-template-columns: 1fr 1fr; }}
            table {{ font-size: 0.85em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 CivicPulse AI Model Evaluation</h1>
            <p>OpenAI CLIP ViT-L/14 Zero-Shot Civic Issue Detection — Accuracy Report</p>
            <p class="timestamp">Generated: {timestamp}</p>
        </div>

        <!-- Key Metrics -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="value green">{metrics['priority_accuracy']}%</div>
                <div class="label">Priority Accuracy</div>
            </div>
            <div class="stat-card">
                <div class="value blue">{metrics['class_accuracy']}%</div>
                <div class="label">Class Accuracy</div>
            </div>
            <div class="stat-card">
                <div class="value purple">{metrics['total_samples']}</div>
                <div class="label">Total Test Samples</div>
            </div>
            <div class="stat-card">
                <div class="value yellow">{metrics['priority_correct']}/{metrics['total_samples']}</div>
                <div class="label">Priority Matches</div>
            </div>
        </div>

        <!-- Model Info -->
        <div class="section">
            <h2>📋 Model Information</h2>
            <div class="model-info">
                <div><div class="label">Model</div><div class="value">OpenAI CLIP ViT-L/14</div></div>
                <div><div class="label">Approach</div><div class="value">Zero-Shot Image Classification</div></div>
                <div><div class="label">Custom Classes</div><div class="value">12 Severity-Aware Civic Issue Categories</div></div>
                <div><div class="label">Priority Levels</div><div class="value">High / Medium / Low / None</div></div>
                <div><div class="label">Framework</div><div class="value">OpenAI CLIP + FastAPI</div></div>
                <div><div class="label">Confidence Threshold</div><div class="value">0.10 (10%)</div></div>
            </div>
        </div>

        <!-- Confusion Matrix -->
        <div class="section">
            <h2>📊 Priority Confusion Matrix</h2>
            <p style="color:#94a3b8;margin-bottom:16px;">Rows = Actual Priority, Columns = Predicted Priority. Green = correct, Red = incorrect.</p>
            <table>
                <tr>
                    <th>Actual \\ Predicted</th>
                    {''.join(f'<th style="text-align:center;text-transform:capitalize;">{p}</th>' for p in priority_labels)}
                </tr>
                {cm_rows}
            </table>
        </div>

        <!-- Per-Class Metrics -->
        <div class="section">
            <h2>🏷️ Per-Class Performance</h2>
            <table>
                <tr>
                    <th>Class</th><th>Priority</th><th style="text-align:center;">Precision</th>
                    <th style="text-align:center;">Recall</th><th style="text-align:center;">F1-Score</th>
                    <th style="text-align:center;">TP</th><th style="text-align:center;">FP</th><th style="text-align:center;">FN</th>
                </tr>
                {class_rows}
            </table>
        </div>

        <!-- Detailed Results -->
        <div class="section">
            <h2>🔍 Detailed Test Results</h2>
            <table>
                <tr>
                    <th>#</th><th>Image Description</th><th>Expected Class</th><th>Predicted Class</th>
                    <th style="text-align:center;">Class</th><th>Expected Priority</th><th>Predicted Priority</th>
                    <th style="text-align:center;">Priority</th><th style="text-align:center;">Confidence</th>
                </tr>
                {result_rows}
            </table>
        </div>

        <div class="footer">
            <p>CivicPulse AI Evaluation Report — Computer Vision for Civic Issue Prioritization</p>
            <p>Model: OpenAI CLIP ViT-L/14 | Dataset: {metrics['total_samples']} curated test images</p>
        </div>
    </div>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n📄 HTML report saved to: {output_path}")


def main():
    print("=" * 70)
    print("  CivicPulse AI Model Evaluation")
    print("  OpenAI CLIP ViT-L/14 — Zero-Shot Civic Issue Detection")
    print("=" * 70)

    # Load model
    import clip
    import torch
    print("\n🔄 Loading OpenAI CLIP ViT-L/14 model...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    clip_model, preprocess = clip.load("ViT-L/14", device=device)
    text_tokens = clip.tokenize(CLIP_CLASSES).to(device)
    
    print(f"✅ Model loaded. Evaluated classes: {[CLIP_CLASS_TO_SHORT[c] for c in CLIP_CLASSES]}")

    # Run tests
    results = []
    print(f"\n📸 Running inference on {len(TEST_DATASET)} test images...\n")

    for i, (url, expected_class, expected_priority, description) in enumerate(TEST_DATASET, 1):
        print(f"  [{i}/{len(TEST_DATASET)}] {description[:50]:<50s} ... ", end="", flush=True)
        try:
            img = download_image(url)
            pred_class, pred_priority, confidence, all_dets = run_inference((clip_model, preprocess, text_tokens), img)

            priority_match = pred_priority == expected_priority
            class_match = pred_class == expected_class

            status = "✅" if priority_match else "❌"
            print(f"{status}  pred={pred_class:<25s} priority={pred_priority:<8s} conf={confidence:.2f}")

            results.append({
                "url": url,
                "description": description,
                "expected_class": expected_class,
                "expected_priority": expected_priority,
                "predicted_class": pred_class,
                "predicted_priority": pred_priority,
                "confidence": confidence,
                "priority_match": priority_match,
                "class_match": class_match,
                "all_detections": all_dets,
            })
        except Exception as e:
            print(f"⚠️  FAILED: {e}")
            results.append({
                "url": url,
                "description": description,
                "expected_class": expected_class,
                "expected_priority": expected_priority,
                "predicted_class": "error",
                "predicted_priority": "none",
                "confidence": 0.0,
                "priority_match": False,
                "class_match": False,
                "all_detections": [],
                "error": str(e),
            })

    # Compute metrics
    metrics = compute_metrics(results)

    # Print summary
    print("\n" + "=" * 70)
    print("  📊 EVALUATION SUMMARY")
    print("=" * 70)
    print(f"  Total Test Samples:    {metrics['total_samples']}")
    print(f"  Priority Accuracy:     {metrics['priority_accuracy']}%  ({metrics['priority_correct']}/{metrics['total_samples']})")
    print(f"  Class Accuracy:        {metrics['class_accuracy']}%  ({metrics['class_correct']}/{metrics['total_samples']})")
    print()
    print("  Per-Class Metrics:")
    print(f"  {'Class':<25s} {'Precision':>10s} {'Recall':>10s} {'F1':>10s}")
    print(f"  {'-'*55}")
    for cls, m in sorted(metrics["class_metrics"].items()):
        print(f"  {cls.title():<25s} {m['precision']*100:>9.1f}% {m['recall']*100:>9.1f}% {m['f1']*100:>9.1f}%")
    print("=" * 70)

    # Save JSON results
    json_path = os.path.join(os.path.dirname(__file__), "evaluation_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"metrics": metrics, "results": results}, f, indent=2, default=str)
    print(f"\n💾 JSON results saved to: {json_path}")

    # Generate HTML report
    html_path = os.path.join(os.path.dirname(__file__), "evaluation_report.html")
    generate_html_report(results, metrics, html_path)

    print(f"\n🎉 Done! Open {html_path} in your browser to view the report.")


if __name__ == "__main__":
    main()
