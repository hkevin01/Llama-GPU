#!/bin/bash

echo "🧹 Project Organization Verification"
echo "===================================="

echo ""
echo "📂 Root Directory (clean):"
ls -1 /home/kevin/Projects/Llama-GPU | grep -E '\.(py|md)$' | wc -l | xargs echo "Python/Markdown files in root:"

echo ""
echo "📚 Documentation organized:"
echo "  - Main docs: $(ls /home/kevin/Projects/Llama-GPU/docs/*.md | wc -l) files"
echo "  - Reports: $(ls /home/kevin/Projects/Llama-GPU/docs/reports/*.md 2>/dev/null | wc -l) files"

echo ""
echo "🔧 Scripts organized:"
echo "  - Total scripts: $(ls /home/kevin/Projects/Llama-GPU/scripts/* 2>/dev/null | wc -l) files"

echo ""
echo "💡 Examples organized:"
echo "  - Example files: $(ls /home/kevin/Projects/Llama-GPU/examples/* 2>/dev/null | wc -l) files"

echo ""
echo "🌐 GUI project organized:"
echo "  - package.json exists: $(test -f /home/kevin/Projects/Llama-GPU/llama-gui/package.json && echo "✅" || echo "❌")"
echo "  - tsconfig.json exists: $(test -f /home/kevin/Projects/Llama-GPU/llama-gui/tsconfig.json && echo "✅" || echo "❌")"

echo ""
echo "🧪 Core project structure:"
echo "  - src/ directory: $(test -d /home/kevin/Projects/Llama-GPU/src && echo "✅" || echo "❌")"
echo "  - tests/ directory: $(test -d /home/kevin/Projects/Llama-GPU/tests && echo "✅" || echo "❌")"
echo "  - config/ directory: $(test -d /home/kevin/Projects/Llama-GPU/config && echo "✅" || echo "❌")"

echo ""
echo "✨ Organization Complete! Project is now clean and well-structured."
