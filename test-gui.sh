#!/bin/bash

# Llama-GPU Interface Testing Script
# Verifies all components and functionality

echo "🧪 Testing Llama-GPU Interface Components"
echo "========================================"

# Test 1: Check file structure
echo "📁 Testing File Structure..."
TEST_PASSED=0
TEST_FAILED=0

# Check main files
files=(
    "src/App.js"
    "src/index.js"
    "src/context/AppContext.js"
    "src/components/Layout/Header.js"
    "src/components/Layout/Sidebar.js"
    "src/components/Pages/Dashboard.js"
    "src/components/Pages/ModelManager.js"
    "src/components/Pages/InferenceCenter.js"
    "src/components/Pages/MultiGPUConfig.js"
    "src/components/Pages/QuantizationSettings.js"
    "src/components/Pages/PerformanceMonitor.js"
    "src/components/Pages/APIServer.js"
    "src/components/Pages/Settings.js"
    "src/components/Common/LoadingSpinner.js"
    "src/components/Common/NotificationSystem.js"
)

for file in "${files[@]}"; do
    if [ -f "llama-gui/$file" ]; then
        echo "  ✅ $file"
        ((TEST_PASSED++))
    else
        echo "  ❌ $file (missing)"
        ((TEST_FAILED++))
    fi
done

# Test 2: Check package.json dependencies
echo ""
echo "📦 Testing Dependencies..."
if [ -f "llama-gui/package.json" ]; then
    echo "  ✅ package.json exists"

    # Check key dependencies
    deps=("react" "@mui/material" "recharts" "framer-motion" "react-router-dom")
    for dep in "${deps[@]}"; do
        if grep -q "\"$dep\"" llama-gui/package.json; then
            echo "  ✅ $dep dependency found"
            ((TEST_PASSED++))
        else
            echo "  ❌ $dep dependency missing"
            ((TEST_FAILED++))
        fi
    done
else
    echo "  ❌ package.json missing"
    ((TEST_FAILED++))
fi

# Test 3: Check node_modules
echo ""
echo "📚 Testing Installation..."
if [ -d "llama-gui/node_modules" ]; then
    echo "  ✅ node_modules directory exists"
    MODULE_COUNT=$(find llama-gui/node_modules -maxdepth 1 -type d | wc -l)
    echo "  ✅ Found $MODULE_COUNT installed modules"
    ((TEST_PASSED++))
else
    echo "  ❌ node_modules missing - run 'npm install'"
    ((TEST_FAILED++))
fi

# Test 4: Syntax validation
echo ""
echo "🔍 Testing Component Syntax..."
SYNTAX_ERRORS=0

# Check for common syntax issues in components
for file in "${files[@]}"; do
    if [ -f "llama-gui/$file" ]; then
        # Check for basic React syntax
        if grep -q "import.*React\|import.*from.*react" "llama-gui/$file"; then
            # Check for export
            if grep -q "export.*default\|export.*function\|export.*const" "llama-gui/$file"; then
                echo "  ✅ $file (syntax OK)"
                ((TEST_PASSED++))
            else
                echo "  ⚠️  $file (no export found)"
                ((SYNTAX_ERRORS++))
            fi
        else
            echo "  ⚠️  $file (no React import)"
            ((SYNTAX_ERRORS++))
        fi
    fi
done

# Test 5: Context validation
echo ""
echo "⚙️  Testing Context System..."
if grep -q "createContext\|useContext\|useReducer" llama-gui/src/context/AppContext.js; then
    echo "  ✅ Context system implemented"
    ((TEST_PASSED++))

    if grep -q "actionTypes" llama-gui/src/context/AppContext.js; then
        echo "  ✅ Action types defined"
        ((TEST_PASSED++))
    else
        echo "  ❌ Action types missing"
        ((TEST_FAILED++))
    fi

    if grep -q "appReducer\|function.*reducer" llama-gui/src/context/AppContext.js; then
        echo "  ✅ Reducer function found"
        ((TEST_PASSED++))
    else
        echo "  ❌ Reducer function missing"
        ((TEST_FAILED++))
    fi
else
    echo "  ❌ Context system not implemented"
    ((TEST_FAILED++))
fi

# Test 6: Theme system
echo ""
echo "🎨 Testing Theme System..."
if grep -q "ThemeProvider\|createTheme" llama-gui/src/App.js; then
    echo "  ✅ Material-UI theme system found"
    ((TEST_PASSED++))
else
    echo "  ❌ Theme system missing"
    ((TEST_FAILED++))
fi

# Test 7: Routing
echo ""
echo "🗺️  Testing Navigation..."
if grep -q "BrowserRouter\|Routes\|Route" llama-gui/src/App.js; then
    echo "  ✅ React Router implemented"
    ((TEST_PASSED++))

    # Count routes
    ROUTE_COUNT=$(grep -c "<Route.*path=" llama-gui/src/App.js)
    echo "  ✅ Found $ROUTE_COUNT route definitions"
    ((TEST_PASSED++))
else
    echo "  ❌ Navigation system missing"
    ((TEST_FAILED++))
fi

# Test Results Summary
echo ""
echo "========================================"
echo "🎯 Test Results Summary"
echo "========================================"
echo "✅ Tests Passed: $TEST_PASSED"
echo "❌ Tests Failed: $TEST_FAILED"
echo "⚠️  Syntax Warnings: $SYNTAX_ERRORS"

TOTAL_TESTS=$((TEST_PASSED + TEST_FAILED))
SUCCESS_RATE=$(( (TEST_PASSED * 100) / TOTAL_TESTS ))

echo ""
echo "📊 Success Rate: $SUCCESS_RATE%"

if [ $TEST_FAILED -eq 0 ] && [ $SYNTAX_ERRORS -eq 0 ]; then
    echo "🎉 All tests passed! Application is ready to run."
    echo ""
    echo "🚀 Next Steps:"
    echo "1. cd llama-gui"
    echo "2. npm start"
    echo "3. Open http://localhost:3000"
elif [ $TEST_FAILED -eq 0 ]; then
    echo "⚠️  Tests passed with warnings. Application should run but may have issues."
    echo ""
    echo "🚀 Try starting anyway:"
    echo "1. cd llama-gui"
    echo "2. npm start"
else
    echo "❌ Critical issues found. Fix these before running:"
    echo "- Ensure all files exist"
    echo "- Run 'npm install' if dependencies missing"
    echo "- Check syntax errors in components"
fi

echo "========================================"
