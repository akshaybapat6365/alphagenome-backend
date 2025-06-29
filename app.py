import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'AlphaGenome Backend',
        'version': '1.0.0'
    })

@app.route('/api/analyze_snps', methods=['POST', 'OPTIONS'])
def analyze_snps():
    """Analyze SNPs - simplified version without AlphaGenome"""
    
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        snps = data.get('snps', [])
        api_key = os.environ.get('ALPHAGENOME_API_KEY')
        
        results = []
        
        for snp in snps:
            # Simplified mock analysis
            position = int(snp.get('position', 0))
            
            # Mock scoring based on position
            base_score = (position % 1000) / 1000.0
            chromosome_factor = int(snp.get('chromosome', 1)) * 0.01
            pathogenicity = min(base_score * 0.7 + chromosome_factor + 0.1, 0.95)
            
            if pathogenicity > 0.8:
                effect = "High impact: Likely pathogenic variant"
            elif pathogenicity > 0.5:
                effect = "Moderate impact: Possible functional consequences"
            else:
                effect = "Low impact: Likely benign variant"
            
            results.append({
                'rsId': snp['rsId'],
                'chromosome': snp['chromosome'],
                'position': snp['position'],
                'genotype': snp['genotype'],
                'predictions': {
                    'pathogenicity': round(pathogenicity, 3),
                    'effect': effect,
                    'confidence': 0.75,
                    'details': {
                        'model_version': 'AlphaGenome-Mock-1.0',
                        'api_key_present': bool(api_key)
                    }
                }
            })
        
        return jsonify({
            'results': results,
            'metadata': {
                'total_variants': len(results),
                'backend_status': 'operational',
                'alphagenome_available': False
            }
        })
        
    except Exception as e:
        logger.error(f"Error in analyze_snps: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        'service': 'AlphaGenome Backend API',
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'analyze': '/api/analyze_snps'
        },
        'deployment': 'Render',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)