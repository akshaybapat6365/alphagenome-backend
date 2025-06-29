import os
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/')
def home():
    return jsonify({"status": "AlphaGenome Backend Running", "version": "1.0.0"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/analyze_snps', methods=['POST', 'OPTIONS'])
def analyze_snps():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        snps = data.get('snps', [])
        api_key = os.environ.get('ALPHAGENOME_API_KEY')
        
        results = []
        for snp in snps:
            position = int(snp.get('position', 0))
            pathogenicity = min((position % 1000) / 1000.0 * 0.8 + 0.1, 0.95)
            
            results.append({
                'rsId': snp['rsId'],
                'chromosome': snp['chromosome'],
                'position': snp['position'],
                'genotype': snp['genotype'],
                'predictions': {
                    'pathogenicity': round(pathogenicity, 3),
                    'effect': 'Mock analysis (Backend operational)',
                    'confidence': 0.75,
                    'details': {
                        'api_key_present': bool(api_key)
                    }
                }
            })
        
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)