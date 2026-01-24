"""
Drug contraindications endpoint
"""
from flask import Blueprint, request, jsonify
from pydantic import BaseModel, Field, ValidationError as PydanticValidationError
from typing import List

from App.observability.logger import get_logger
from App.utils.exceptions import ValidationError
from App.config.feature_flags import FeatureFlags

logger = get_logger(__name__)

bp = Blueprint('contraindications', __name__)


class ContraindicationCheckRequest(BaseModel):
    """Request model for contraindication check"""
    drug_names: List[str] = Field(..., min_items=1, max_items=10, description="List of drug names to check")
    patient_conditions: List[str] = Field(default=[], description="List of patient conditions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "drug_names": ["Aspirin", "Warfarin"],
                "patient_conditions": ["bleeding disorder"]
            }
        }


@bp.route('/contraindications/check', methods=['POST'])
def check_contraindications():
    """
    Check drug contraindications endpoint (stub)
    
    Returns:
        JSON response with contraindication analysis
    """
    logger.info('Contraindication check requested')
    
    # Check feature flag
    if not FeatureFlags.is_enabled('contraindications'):
        logger.warning('Contraindications feature is disabled')
        return jsonify({
            'error': 'Feature disabled',
            'message': 'Contraindications check is currently disabled'
        }), 503
    
    try:
        # Validate request
        data = request.get_json()
        if not data:
            raise ValidationError('Request body is required')
        
        request_model = ContraindicationCheckRequest(**data)
        logger.info(f'Contraindication check: drugs={request_model.drug_names}, conditions={request_model.patient_conditions}')
        
        # TODO: Implement contraindication checking logic
        # This is a placeholder implementation
        results = {
            'drug_names': request_model.drug_names,
            'patient_conditions': request_model.patient_conditions,
            'contraindications': [],
            'warnings': [],
            'message': 'Contraindication check is not yet implemented'
        }
        
        return jsonify(results), 200
        
    except PydanticValidationError as e:
        logger.warning(f'Validation error: {e}')
        raise ValidationError(f'Invalid request: {e.errors()}')
    except ValidationError as e:
        logger.warning(f'Validation error: {e.message}')
        return jsonify({'error': 'Validation Error', 'message': e.message}), e.status_code
    except Exception as e:
        logger.error(f'Unexpected error in contraindication check: {e}', exc_info=True)
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500
