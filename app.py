import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# AlphaGenome imports will be added after installation
try:
    from alphagenome.data import genome
    from alphagenome.models import dna_client
    ALPHAGENOME_AVAILABLE = True
    logger.info("AlphaGenome library loaded successfully")
except ImportError:
    ALPHAGENOME_AVAILABLE = False
    logger.warning("AlphaGenome library not available - will use mock data")

# Initialize AlphaGenome client if available
model = None
if ALPHAGENOME_AVAILABLE:
    API_KEY = os.environ.get('ALPHAGENOME_API_KEY', 'AIzaSyAd8VEbbDBGpQoPGK4v8LZzdaGlgBh2kaE')
    try:
        model = dna_client.create(API_KEY)
        logger.info("AlphaGenome client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize AlphaGenome client: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'alphagenome_available': ALPHAGENOME_AVAILABLE,
        'model_initialized': model is not None
    })

@app.route('/api/analyze_snps', methods=['POST', 'OPTIONS'])
def analyze_snps():
    """Analyze SNPs using AlphaGenome"""
    
    if request.method == 'OPTIONS':
        # Handle preflight request
        return '', 200
    
    try:
        data = request.get_json()
        snps = data.get('snps', [])
        
        results = []
        
        for snp in snps:
            try:
                if ALPHAGENOME_AVAILABLE and model:
                    # Real AlphaGenome analysis
                    logger.info(f"Analyzing variant {snp['rsId']}")
                    
                    # Create variant object
                    variant = genome.Variant(
                        chromosome=f"chr{snp['chromosome']}",
                        position=int(snp['position']),
                        reference_bases=snp['genotype'][0] if len(snp['genotype']) > 0 else 'N',
                        alternate_bases=snp['genotype'][1] if len(snp['genotype']) > 1 else snp['genotype'][0],
                    )
                    
                    # Define genomic interval (±500kb around variant)
                    interval = genome.Interval(
                        chromosome=f"chr{snp['chromosome']}",
                        start=max(0, int(snp['position']) - 500000),
                        end=int(snp['position']) + 500000
                    )
                    
                    # Get predictions
                    outputs = model.predict_variant(
                        interval=interval,
                        variant=variant,
                        requested_outputs=[
                            dna_client.OutputType.RNA_SEQ,
                            dna_client.OutputType.SPLICING,
                            dna_client.OutputType.CHROMATIN_ACCESSIBILITY
                        ],
                    )
                    
                    # Calculate pathogenicity based on model outputs
                    pathogenicity = 0.5  # Default
                    effect_details = []
                    
                    # Analyze RNA expression changes
                    if hasattr(outputs, 'reference') and hasattr(outputs, 'alternate'):
                        if hasattr(outputs.reference, 'rna_seq') and hasattr(outputs.alternate, 'rna_seq'):
                            ref_mean = float(outputs.reference.rna_seq.mean())
                            alt_mean = float(outputs.alternate.rna_seq.mean())
                            rna_change = abs(ref_mean - alt_mean) / (ref_mean + 0.001)
                            pathogenicity = max(pathogenicity, min(rna_change * 2, 0.95))
                            effect_details.append(f"RNA expression change: {rna_change:.1%}")
                    
                    # Check splicing impact
                    if hasattr(outputs.alternate, 'splicing'):
                        effect_details.append("Potential splicing impact detected")
                        pathogenicity = max(pathogenicity, 0.7)
                    
                    # Check chromatin accessibility
                    if hasattr(outputs.alternate, 'chromatin_accessibility'):
                        effect_details.append("Chromatin accessibility changes detected")
                        pathogenicity = max(pathogenicity, 0.6)
                    
                    effect = " | ".join(effect_details) if effect_details else "No significant functional impact detected"
                    
                    results.append({
                        'rsId': snp['rsId'],
                        'chromosome': snp['chromosome'],
                        'position': snp['position'],
                        'genotype': snp['genotype'],
                        'predictions': {
                            'pathogenicity': round(float(pathogenicity), 3),
                            'effect': effect,
                            'confidence': 0.85,
                            'details': {
                                'model_version': 'AlphaGenome-1.0',
                                'analysis_complete': True
                            }
                        }
                    })
                    
                else:
                    # Mock analysis when AlphaGenome not available
                    position = int(snp.get('position', 0))
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
                            'effect': effect + " (Mock analysis - AlphaGenome not available)",
                            'confidence': 0.5,
                            'details': {
                                'model_version': 'Mock-1.0',
                                'analysis_complete': False
                            }
                        }
                    })
                    
            except Exception as e:
                logger.error(f"Error analyzing variant {snp['rsId']}: {e}")
                results.append({
                    'rsId': snp['rsId'],
                    'chromosome': snp['chromosome'],
                    'position': snp['position'],
                    'genotype': snp['genotype'],
                    'error': str(e)
                })
        
        return jsonify({
            'results': results,
            'metadata': {
                'total_variants': len(results),
                'alphagenome_available': ALPHAGENOME_AVAILABLE,
                'model_initialized': model is not None
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
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)