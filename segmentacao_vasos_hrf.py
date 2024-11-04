import os
import cv2
import numpy as np
from tqdm import tqdm
from segmentacao_vasos_stare_drive import RetinalVesselSegmentation

def main():
    # Configuração dos diretórios para HRF
    hrf_base = 'datasets/HRF'
    input_dir = os.path.join(hrf_base, 'images')
    output_dir = 'resultados/segmentacao/HRF'
    
    print(f"\nProcessando dataset HRF")
    
    # Cria instância do processador com parâmetros ajustados para HRF
    processor = RetinalVesselSegmentation(
        input_dir=input_dir,
        output_dir=output_dir
    )
    
    # Ajusta parâmetros específicos para imagens HRF (que são maiores)
    processor.params.update({
        'gaussian_kernel': 7,  # Kernel maior devido à resolução mais alta
        'gaussian_sigma': 1,
        'blackhat_kernel': 40, 
        'initial_threshold': 15
    })
    
    # Processa o dataset
    processor.process_dataset()

if __name__ == "__main__":
    main()
