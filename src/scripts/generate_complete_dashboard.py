#!/usr/bin/env python3
"""
Complete Chart Generation System - Sistema completo com animações e métricas avançadas

Gera todos os gráficos:
- Stats com comparações temporais
- Linguagens com animações
- Atividade com trends
- Streak com progresso visual
- Tier com contexto
- Roadmap de estudos
- Goals tracker
- Learning analytics
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.generators.enhanced_svg_renderer import EnhancedSVGRenderer
from src.generators.roadmap_generator import RoadmapGenerator
from src.generators.career_timeline_generator import CareerTimelineGenerator
from src.generators.activity_calendar_generator import ActivityCalendarGenerator


def load_data(file_path: Path, default: dict = None) -> dict:
    """Carrega dados JSON com fallback."""
    if file_path.exists():
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Warning: Could not load {file_path}: {e}")
    return default or {}


def main():
    print("🎨 " + "=" * 60)
    print("   COMPLETE PROFILE DASHBOARD GENERATOR")
    print("   With animations, trends, and learning roadmap")
    print("=" * 62)
    
    # Load all data
    metrics_path = Path("data/metrics.json")
    history_path = Path("data/history.json")
    
    if not metrics_path.exists():
        print("\n❌ Error: data/metrics.json not found")
        print("   Run: python3 src/scripts/daily_metrics.py first")
        return 1
    
    print("\n📊 Loading data...")
    metrics = load_data(metrics_path)
    history = load_data(history_path, {"monthly_snapshots": []})
    
    print(f"   ✓ Metrics loaded: {len(metrics)} keys")
    print(f"   ✓ History loaded: {len(history.get('monthly_snapshots', []))} snapshots")
    
    # Initialize renderers
    print("\n🎨 Initializing renderers...")
    enhanced_renderer = EnhancedSVGRenderer()
    roadmap_generator = RoadmapGenerator()
    career_generator = CareerTimelineGenerator()
    activity_calendar = ActivityCalendarGenerator()
    
    charts_generated = []
    errors = []
    
    # Chart configurations
    chart_configs = [
        ("Stats Hero", "generate_stats_hero", "stats_hero.svg", enhanced_renderer, [metrics, history]),
        ("Language Chart", "generate_language_chart", "language_chart.svg", enhanced_renderer, [metrics]),
        ("Performance Comparison", "generate_performance_comparison", "performance_comparison.svg", enhanced_renderer, [metrics, history]),
        ("Featured Projects", "generate_featured_projects", "featured_projects.svg", enhanced_renderer, []),
        ("Activity Calendar", "generate_activity_calendar", "activity_calendar.svg", activity_calendar, [metrics]),
        ("Goals Tracker", "generate_goals_tracker", "goals_tracker.svg", roadmap_generator, []),
        ("Learning Stats", "generate_learning_stats", "learning_stats.svg", roadmap_generator, [metrics]),
        ("Career Timeline", "generate_timeline", "career_timeline.svg", career_generator, []),
    ]
    
    print("\n🚀 Generating enhanced charts...")
    print("-" * 62)
    
    start_time = datetime.now()
    
    for name, method, filename, renderer, args in chart_configs:
        try:
            print(f"\n📊 {name}...", end=" ", flush=True)
            generator = getattr(renderer, method)
            path = generator(*args, filename)
            
            # Verify file
            if Path(path).exists() and Path(path).stat().st_size > 0:
                size_kb = Path(path).stat().st_size / 1024
                print(f"✅ ({size_kb:.1f} KB)")
                charts_generated.append(filename)
            else:
                print("❌ Empty file")
                errors.append(f"{name}: Empty file generated")
        except Exception as e:
            print(f"❌ Error")
            errors.append(f"{name}: {str(e)}")
            import traceback
            print(f"   Details: {traceback.format_exc()}")
    
    duration = (datetime.now() - start_time).total_seconds()
    
    # Summary
    print("\n" + "=" * 62)
    print(f"✨ Generation Complete!")
    print(f"   • Charts generated: {len(charts_generated)}/{len(chart_configs)}")
    print(f"   • Duration: {duration:.2f}s")
    print(f"   • Output: assets/")
    
    if charts_generated:
        print(f"\n📁 Generated files:")
        for chart in charts_generated:
            print(f"   ✓ {chart}")
    
    if errors:
        print(f"\n⚠️  Errors encountered:")
        for error in errors:
            print(f"   ✗ {error}")
    
    # Feature summary
    print("\n🎯 Features:")
    print("   ✓ CSS animations (fadeIn, slideUp, scaleIn, pulse, glow)")
    print("   ✓ Temporal comparisons (vs previous month)")
    print("   ✓ Contextual tier system with descriptions")
    print("   ✓ Progress tracking with milestones")
    print("   ✓ Learning roadmap with skill levels")
    print("   ✓ Dynamic goals with deadlines")
    print("   ✓ Estimated learning hours")
    print("   ✓ Self-contained (no external dependencies)")
    
    print("\n💡 Next steps:")
    print("   1. Check assets/*.svg files")
    print("   2. Update data/roadmap.json with your goals")
    print("   3. Customize skill levels and targets")
    print("   4. Deploy to your GitHub profile!")
    
    print("\n" + "=" * 62)
    
    return 0 if len(errors) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
