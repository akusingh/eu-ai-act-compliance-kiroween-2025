#!/usr/bin/env python3
"""
Simple web UI for EU AI Act Compliance Agent
Perfect for hackathon demo - single file, no complex setup
"""

from flask import Flask, render_template_string, request, jsonify
import json
import logging
from datetime import datetime
from pathlib import Path
from src.evaluation import AgentEvaluator
from src.config import Config
from src.observability import setup_logging

# Setup logging for web demo
setup_logging("INFO")
logger = logging.getLogger(__name__)

# Create logs directory
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Add file handler for web UI logs
web_log_file = logs_dir / f"web_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
file_handler = logging.FileHandler(web_log_file)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(file_handler)

app = Flask(__name__)

logger.info("Web demo starting up")

# Initialize evaluator once (reuse orchestrator)
evaluator = None

def get_evaluator():
    """Get or create evaluator instance."""
    global evaluator
    if evaluator is None:
        evaluator = AgentEvaluator()
    return evaluator

# HTML template with embedded CSS
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EU AI Act Compliance Agent - Kiroween 2025</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .agent-step { transition: all 0.3s ease; }
        .agent-active { background: #fef3c7; border-left: 4px solid #f59e0b; }
        .agent-complete { background: #d1fae5; border-left: 4px solid #10b981; }
        .risk-prohibited { background: #fee2e2; color: #991b1b; }
        .risk-high { background: #fef3c7; color: #92400e; }
        .risk-limited { background: #dbeafe; color: #1e40af; }
        .risk-minimal { background: #d1fae5; color: #065f46; }
    </style>
</head>
<body class="bg-gray-50">
    <div class="container mx-auto px-4 py-8 max-w-6xl">
        <!-- Header -->
        <div class="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-8 mb-8 shadow-lg">
            <h1 class="text-4xl font-bold mb-2">🏆 EU AI Act Compliance Agent</h1>
            <p class="text-xl mb-4">Kiroween Hackathon 2025</p>
            <div class="flex gap-4 text-sm">
                <span class="bg-white/20 px-3 py-1 rounded">Google ADK</span>
                <span class="bg-white/20 px-3 py-1 rounded">Gemini 2.0</span>
                <span class="bg-white/20 px-3 py-1 rounded">Multi-Agent</span>
                <span class="bg-white/20 px-3 py-1 rounded">87.5% Accuracy</span>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- Left: Input Form -->
            <div class="bg-white rounded-lg shadow-lg p-6">
                <h2 class="text-2xl font-bold mb-4">AI System Information</h2>
                
                <form id="assessmentForm" class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium mb-1">System Name</label>
                        <input type="text" id="system_name" class="w-full border rounded px-3 py-2" 
                               placeholder="e.g., Loan Approval System" required>
                    </div>
                    
                    <div>
                        <label class="block text-sm font-medium mb-1">Use Case</label>
                        <textarea id="use_case" class="w-full border rounded px-3 py-2" rows="3"
                                  placeholder="Describe what the AI system does..." required></textarea>
                    </div>
                    
                    <div>
                        <label class="block text-sm font-medium mb-1">Data Types (comma-separated)</label>
                        <input type="text" id="data_types" class="w-full border rounded px-3 py-2"
                               placeholder="e.g., financial, personal_data, biometric">
                    </div>
                    
                    <div>
                        <label class="block text-sm font-medium mb-1">Decision Impact</label>
                        <select id="decision_impact" class="w-full border rounded px-3 py-2">
                            <option value="significant">Significant</option>
                            <option value="moderate">Moderate</option>
                            <option value="minimal">Minimal</option>
                        </select>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="flex items-center">
                                <input type="checkbox" id="autonomous_decision" class="mr-2">
                                <span class="text-sm">Autonomous Decision</span>
                            </label>
                        </div>
                        <div>
                            <label class="flex items-center">
                                <input type="checkbox" id="human_oversight" class="mr-2" checked>
                                <span class="text-sm">Human Oversight</span>
                            </label>
                        </div>
                    </div>
                    
                    <div>
                        <label class="block text-sm font-medium mb-1">Error Consequences</label>
                        <input type="text" id="error_consequences" class="w-full border rounded px-3 py-2"
                               placeholder="e.g., Severe - affects credit access">
                    </div>
                    
                    <button type="submit" 
                            class="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition">
                        🚀 Assess Compliance
                    </button>
                </form>
                
                <!-- Quick Examples -->
                <div class="mt-6 pt-6 border-t">
                    <p class="text-sm font-medium mb-2">Quick Examples:</p>
                    <div class="space-y-2">
                        <button onclick="loadExample('loan')" 
                                class="text-sm text-blue-600 hover:underline block">
                            💰 Loan Approval System (High Risk)
                        </button>
                        <button onclick="loadExample('chatbot')" 
                                class="text-sm text-blue-600 hover:underline block">
                            💬 Customer Chatbot (Limited Risk)
                        </button>
                        <button onclick="loadExample('social')" 
                                class="text-sm text-blue-600 hover:underline block">
                            🚫 Social Credit System (Prohibited)
                        </button>
                    </div>
                </div>
            </div>

            <!-- Right: Results -->
            <div class="bg-white rounded-lg shadow-lg p-6">
                <h2 class="text-2xl font-bold mb-4">Assessment Results</h2>
                
                <!-- Loading State -->
                <div id="loadingState" class="hidden">
                    <div class="space-y-3">
                        <div class="agent-step p-3 rounded border" id="step1">
                            <div class="flex items-center">
                                <span class="text-2xl mr-2">⚙️</span>
                                <span class="font-medium">Information Gathering</span>
                            </div>
                        </div>
                        <div class="agent-step p-3 rounded border" id="step2">
                            <div class="flex items-center">
                                <span class="text-2xl mr-2">⚡</span>
                                <span class="font-medium">Parallel Research (3 agents)</span>
                            </div>
                            <div class="text-sm text-gray-600 ml-10">
                                Recitals • Articles • Annexes
                            </div>
                        </div>
                        <div class="agent-step p-3 rounded border" id="step3">
                            <div class="flex items-center">
                                <span class="text-2xl mr-2">🔄</span>
                                <span class="font-medium">Legal Aggregation</span>
                            </div>
                        </div>
                        <div class="agent-step p-3 rounded border" id="step4">
                            <div class="flex items-center">
                                <span class="text-2xl mr-2">⚖️</span>
                                <span class="font-medium">Compliance Classification</span>
                            </div>
                        </div>
                        <div class="agent-step p-3 rounded border" id="step5">
                            <div class="flex items-center">
                                <span class="text-2xl mr-2">📄</span>
                                <span class="font-medium">Report Generation</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Results State -->
                <div id="resultsState" class="hidden">
                    <div id="riskTier" class="p-4 rounded-lg mb-4 text-center">
                        <div class="text-sm font-medium mb-1">Risk Classification</div>
                        <div id="tierValue" class="text-3xl font-bold"></div>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-4 mb-4">
                        <div class="border rounded p-3">
                            <div class="text-sm text-gray-600">Risk Score</div>
                            <div id="scoreValue" class="text-2xl font-bold"></div>
                        </div>
                        <div class="border rounded p-3">
                            <div class="text-sm text-gray-600">Confidence</div>
                            <div id="confidenceValue" class="text-2xl font-bold"></div>
                        </div>
                    </div>
                    
                    <div class="border rounded p-4 mb-4 bg-blue-50 border-blue-200">
                        <div class="font-semibold mb-3 text-blue-900 flex items-center">
                            <span class="text-lg mr-2">📜</span>
                            <span>Relevant EU AI Act Articles</span>
                        </div>
                        <div id="articlesValue" class="space-y-2"></div>
                    </div>
                    
                    <div class="border rounded p-4 bg-green-50 border-green-200">
                        <div class="font-semibold mb-3 text-green-900 flex items-center">
                            <span class="text-lg mr-2">💡</span>
                            <span>Key Recommendations</span>
                        </div>
                        <div id="recommendationsValue" class="space-y-2"></div>
                    </div>
                    
                    <button onclick="resetForm()" 
                            class="w-full mt-4 bg-gray-200 text-gray-800 py-2 rounded hover:bg-gray-300 transition">
                        Assess Another System
                    </button>
                </div>
                
                <!-- Initial State -->
                <div id="initialState" class="text-center text-gray-500 py-12">
                    <div class="text-6xl mb-4">🤖</div>
                    <p class="text-lg">Fill in the form and click "Assess Compliance"</p>
                    <p class="text-sm mt-2">Multi-agent pipeline will analyze your AI system</p>
                </div>
            </div>
        </div>
        
        <!-- Architecture Info -->
        <div class="mt-8 bg-white rounded-lg shadow-lg p-6">
            <h3 class="text-xl font-bold mb-4">🏗️ System Architecture</h3>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
                <div class="border rounded p-4">
                    <div class="text-3xl font-bold text-blue-600">8</div>
                    <div class="text-sm text-gray-600">Total Agents</div>
                </div>
                <div class="border rounded p-4">
                    <div class="text-3xl font-bold text-purple-600">1,123</div>
                    <div class="text-sm text-gray-600">Indexed Chunks</div>
                </div>
                <div class="border rounded p-4">
                    <div class="text-3xl font-bold text-green-600">87.5%</div>
                    <div class="text-sm text-gray-600">Accuracy</div>
                </div>
                <div class="border rounded p-4">
                    <div class="text-3xl font-bold text-orange-600">~35s</div>
                    <div class="text-sm text-gray-600">Processing Time</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const examples = {
            loan: {
                system_name: "Automated Loan Approval System",
                use_case: "Automated creditworthiness assessment for consumer loans",
                data_types: "financial, personal_data, employment",
                decision_impact: "significant",
                autonomous_decision: true,
                human_oversight: true,
                error_consequences: "Severe - affects credit access"
            },
            chatbot: {
                system_name: "Customer Support Chatbot",
                use_case: "Automated customer service chatbot for product inquiries",
                data_types: "conversation_data, customer_info",
                decision_impact: "minimal",
                autonomous_decision: false,
                human_oversight: true,
                error_consequences: "Minor - can escalate to human"
            },
            social: {
                system_name: "Social Credit Scoring System",
                use_case: "Evaluates citizens' trustworthiness based on social behavior",
                data_types: "social_media, financial, behavioral, biometric",
                decision_impact: "significant",
                autonomous_decision: true,
                human_oversight: false,
                error_consequences: "Severe - affects fundamental rights"
            }
        };
        
        function loadExample(type) {
            const ex = examples[type];
            document.getElementById('system_name').value = ex.system_name;
            document.getElementById('use_case').value = ex.use_case;
            document.getElementById('data_types').value = ex.data_types;
            document.getElementById('decision_impact').value = ex.decision_impact;
            document.getElementById('autonomous_decision').checked = ex.autonomous_decision;
            document.getElementById('human_oversight').checked = ex.human_oversight;
            document.getElementById('error_consequences').value = ex.error_consequences;
        }
        
        function animateSteps() {
            const steps = ['step1', 'step2', 'step3', 'step4', 'step5'];
            let current = 0;
            
            const interval = setInterval(() => {
                if (current > 0) {
                    document.getElementById(steps[current - 1]).classList.remove('agent-active');
                    document.getElementById(steps[current - 1]).classList.add('agent-complete');
                }
                if (current < steps.length) {
                    document.getElementById(steps[current]).classList.add('agent-active');
                    current++;
                } else {
                    clearInterval(interval);
                }
            }, 2000);
        }
        
        function resetForm() {
            document.getElementById('initialState').classList.remove('hidden');
            document.getElementById('resultsState').classList.add('hidden');
            document.getElementById('loadingState').classList.add('hidden');
        }
        
        function toggleDetails(idx) {
            const detailsDiv = document.getElementById(`details-${idx}`);
            const toggleBtn = document.getElementById(`toggle-${idx}`);
            
            if (detailsDiv.classList.contains('hidden')) {
                detailsDiv.classList.remove('hidden');
                toggleBtn.textContent = '- Hide';
            } else {
                detailsDiv.classList.add('hidden');
                toggleBtn.textContent = '+ Details';
            }
        }
        
        document.getElementById('assessmentForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Show loading
            document.getElementById('initialState').classList.add('hidden');
            document.getElementById('resultsState').classList.add('hidden');
            document.getElementById('loadingState').classList.remove('hidden');
            
            // Animate steps
            animateSteps();
            
            // Collect form data
            const data = {
                system_name: document.getElementById('system_name').value,
                use_case: document.getElementById('use_case').value,
                data_types: document.getElementById('data_types').value.split(',').map(s => s.trim()),
                decision_impact: document.getElementById('decision_impact').value,
                autonomous_decision: document.getElementById('autonomous_decision').checked,
                human_oversight: document.getElementById('human_oversight').checked,
                error_consequences: document.getElementById('error_consequences').value,
                affected_groups: "Users"
            };
            
            try {
                const response = await fetch('/assess', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                // Show results after animation
                setTimeout(() => {
                    document.getElementById('loadingState').classList.add('hidden');
                    document.getElementById('resultsState').classList.remove('hidden');
                    
                    // Populate results
                    const tier = result.assessment.tier.toUpperCase().replace('_', ' ');
                    const tierClass = 'risk-' + result.assessment.tier.split('_')[0];
                    
                    document.getElementById('riskTier').className = 'p-4 rounded-lg mb-4 text-center ' + tierClass;
                    document.getElementById('tierValue').textContent = tier;
                    document.getElementById('scoreValue').textContent = result.assessment.score + '/100';
                    
                    // Handle confidence - if already a percentage (>1), use as-is, otherwise multiply by 100
                    const confidence = result.assessment.confidence;
                    const confidencePercent = confidence > 1 ? Math.round(confidence) : Math.round(confidence * 100);
                    document.getElementById('confidenceValue').textContent = confidencePercent + '%';
                    
                    const articles = result.assessment.articles.slice(0, 5);
                    document.getElementById('articlesValue').innerHTML = articles.map(a => 
                        `<div class="flex items-start border-l-2 border-blue-500 pl-3 py-1 bg-white rounded">
                            <span class="mr-2 text-blue-600 mt-0.5">📋</span>
                            <span class="text-sm">${a}</span>
                        </div>`
                    ).join('');
                    
                    const recs = result.report.recommendations?.slice(0, 3) || ['Detailed recommendations available in full report'];
                    document.getElementById('recommendationsValue').innerHTML = recs.map((r, idx) => {
                        let summary, hasDetails = false, details = '';
                        
                        if (typeof r === 'string') {
                            summary = r;
                        } else if (typeof r === 'object') {
                            // Extract summary from various possible fields
                            summary = r.action_item || r.action || r.text || r.recommendation || Object.values(r)[0];
                            
                            // Check if we have detailed fields
                            if (r.priority || r.specific_steps || r.steps || r.timeline_considerations || r.timeline) {
                                hasDetails = true;
                                details = '<div class="mt-2 pl-6 space-y-2 text-xs text-gray-700 bg-gray-50 p-3 rounded">';
                                
                                if (r.priority) {
                                    const priorityColor = r.priority === 'High' ? 'text-red-600 font-bold' : r.priority === 'Medium' ? 'text-yellow-600 font-semibold' : 'text-blue-600';
                                    details += `<div><span class="font-semibold text-gray-900">Priority:</span> <span class="${priorityColor}">${r.priority}</span></div>`;
                                }
                                
                                const steps = r.specific_steps || r.steps;
                                if (steps) {
                                    details += `<div><span class="font-semibold text-gray-900">Implementation Steps:</span>`;
                                    if (Array.isArray(steps)) {
                                        details += '<ol class="mt-1 pl-4 list-decimal space-y-1">';
                                        steps.forEach(step => {
                                            details += `<li>${step}</li>`;
                                        });
                                        details += '</ol>';
                                    } else {
                                        details += `<div class="mt-1 pl-2">${steps}</div>`;
                                    }
                                    details += '</div>';
                                }
                                
                                const timeline = r.timeline_considerations || r.timeline;
                                if (timeline) {
                                    details += `<div><span class="font-semibold text-gray-900">Timeline:</span> <span class="text-blue-700">${timeline}</span></div>`;
                                }
                                
                                details += '</div>';
                            }
                        }
                        
                        // Create expandable recommendation
                        if (hasDetails) {
                            return `
                                <div class="border-l-2 border-green-500 pl-3 py-1 hover:bg-gray-50 transition">
                                    <div class="flex items-start justify-between">
                                        <div class="flex items-start flex-1">
                                            <span class="mr-2 text-green-600 mt-0.5">✓</span>
                                            <span class="text-sm flex-1">${summary}</span>
                                        </div>
                                        <button onclick="toggleDetails(${idx})" 
                                                class="ml-2 text-blue-600 hover:text-blue-800 text-xs font-medium flex-shrink-0 px-2 py-1 rounded hover:bg-blue-50">
                                            <span id="toggle-${idx}">+ Details</span>
                                        </button>
                                    </div>
                                    <div id="details-${idx}" class="hidden">
                                        ${details}
                                    </div>
                                </div>
                            `;
                        } else {
                            return `
                                <div class="flex items-start border-l-2 border-green-500 pl-3 py-1">
                                    <span class="mr-2 text-green-600 mt-0.5">✓</span>
                                    <span class="text-sm">${summary}</span>
                                </div>
                            `;
                        }
                    }).join('');
                }, 10000);
                
            } catch (error) {
                alert('Error: ' + error.message);
                resetForm();
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the web UI."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/assess', methods=['POST'])
def assess():
    """Run compliance assessment."""
    try:
        system_info = request.json
        system_name = system_info.get('system_name', 'Unknown')
        
        logger.info(f"Assessment request received for: {system_name}")
        logger.info(f"Request data: {json.dumps(system_info, indent=2)}")
        
        # Use the same approach as evaluate.py and demo_final.py
        eval_instance = get_evaluator()
        result = eval_instance.orchestrator.assess_system(system_info)
        
        # Log results
        assessment = result.get('assessment', {})
        logger.info(f"Assessment complete for {system_name}")
        logger.info(f"Result: {assessment.get('tier')} - Score: {assessment.get('score')}/100")
        logger.info(f"Response data: {json.dumps(result, indent=2, default=str)}")
        
        return jsonify(result)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Assessment error: {str(e)}")
        logger.error(f"Traceback: {error_details}")
        return jsonify({"error": str(e), "details": error_details}), 500

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🏆 EU AI Act Compliance Agent - Web Demo")
    print("="*80)
    
    # Validate API key
    if not Config.GOOGLE_GENAI_API_KEY:
        print("\n⚠️  ERROR: GOOGLE_GENAI_API_KEY not configured in .env")
        print("Get one at: https://aistudio.google.com/")
        print("\nThe web UI will start, but assessments will fail without an API key.\n")
        logger.warning("Starting without API key configured")
    else:
        print("\n✅ API key configured")
        logger.info("API key configured successfully")
    
    print("\n🌐 Starting web server...")
    print("📱 Open in browser: http://localhost:8080")
    print(f"📝 Logs will be saved to: {web_log_file}")
    print("\n⚡ Ready for hackathon demo!\n")
    
    logger.info("Web server starting on port 8080")
    app.run(debug=True, port=8080)
