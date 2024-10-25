import os
import cv2
import numpy as np
from tqdm import tqdm

class RetinalVesselSegmentation:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Cria pastas para cada etapa intermediária
        self.step_folders = [
            "red_channel", "green_channel", "blue_channel", "mask",
            "blurred", "blackhat", "threshold", "reconstructed"
        ]
        for folder in self.step_folders:
            os.makedirs(os.path.join(output_dir, folder), exist_ok=True)
        
        # Parâmetros do pipeline
        self.params = {
            'gaussian_kernel': 5,
            'gaussian_sigma': 0,
            'blackhat_kernel': 15,
            'initial_threshold': 10
        }

    def _extract_channels(self, image):
        """Extrai os canais vermelho, verde e azul da imagem."""
        return cv2.split(image)

    def _create_mask(self, green_channel):
        """Cria máscara para isolar região de interesse."""
        _, mask = cv2.threshold(green_channel, self.params['initial_threshold'], 255, cv2.THRESH_BINARY)
        return mask

    def _apply_gaussian(self, image):
        """Aplica filtro gaussiano para suavização."""
        kernel_size = self.params['gaussian_kernel']
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), self.params['gaussian_sigma'])

    def _apply_blackhat(self, image):
        """Aplica operação black-hat para realçar vasos."""
        kernel_size = self.params['blackhat_kernel']
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        closed = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        return cv2.subtract(closed, image)

    def _apply_binary_threshold(self, image):
        """Aplica limiarização usando método Otsu."""
        _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary

    def _apply_reconstruction(self, binary):
        """Aplica abertura por reconstrução."""
        kernel = np.ones((3, 3), np.uint8)
        eroded = cv2.erode(binary, kernel, iterations=1)
        return cv2.dilate(eroded, kernel, iterations=1)

    def process_image(self, image, filename):
        """Executa o pipeline completo de segmentação e salva resultados intermediários."""
        # (a) Red channel (b) Green channel (c) Blue channel
        blue, green, red = self._extract_channels(image)
        
        # (d) Mask
        mask = self._create_mask(green)
        
        # (e) After blur
        blurred = self._apply_gaussian(green)
        
        # (f) After black-hat
        blackhat = self._apply_blackhat(blurred)
        
        # (g) After threshold
        threshold = self._apply_binary_threshold(blackhat)
        
        # (h) After reconstruction
        reconstructed = self._apply_reconstruction(threshold)
        
        # Salva cada etapa intermediária em sua respectiva pasta
        steps = [red, green, blue, mask, blurred, blackhat, threshold, reconstructed]
        for step_img, folder in zip(steps, self.step_folders):
            output_path = os.path.join(self.output_dir, folder, f"{os.path.splitext(filename)[0]}.png")
            cv2.imwrite(output_path, step_img)
        
        # Salva a imagem final combinada na ordem correta
        self.save_combined_result(
            steps,
            filename,
            ["Red", "Green", "Blue", "Mask", "Blurred", "Black-hat", "Threshold", "Reconstructed"]
        )
        
        return reconstructed

    def save_combined_result(self, images, original_filename, step_names):
        """Salva todas as etapas intermediárias em uma única imagem com legendas."""
        combined_image = self._combine_images_with_labels(images, step_names)
        combined_dir = os.path.join(self.output_dir, "imagens_combinadas")
        os.makedirs(combined_dir, exist_ok=True)
        output_filename = f"{os.path.splitext(original_filename)[0]}_combined.png"
        output_path = os.path.join(combined_dir, output_filename)
        cv2.imwrite(output_path, combined_image)
        print(f"Imagem combinada salva em: {output_path}")

    def _combine_images_with_labels(self, images, labels):
        """Combina imagens em duas linhas e adiciona legendas."""
        labeled_images = []
        for img, label in zip(images, labels):
            # Converte a imagem para RGB se for de canal único
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            
            # Redimensiona a imagem para um tamanho padrão
            img = cv2.resize(img, (200, 200))
            
            # Adiciona uma borda inferior para a legenda
            bordered_img = cv2.copyMakeBorder(img, 0, 30, 0, 0, cv2.BORDER_CONSTANT, value=[0, 0, 0])
            
            # Coloca o texto da legenda
            cv2.putText(bordered_img, label, (10, img.shape[0] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            labeled_images.append(bordered_img)
        
        # Divide as imagens em duas linhas
        top_row = cv2.hconcat(labeled_images[:4])
        bottom_row = cv2.hconcat(labeled_images[4:])
        
        # Combina as duas linhas verticalmente
        return cv2.vconcat([top_row, bottom_row])

    def process_dataset(self):
        """Processa todas as imagens do diretório de entrada."""
        print(f"Processando imagens em: {self.input_dir}")
        
        for filename in tqdm(os.listdir(self.input_dir)):
            if filename.endswith(('.ppm', '.tif', '.jpg', '.png')):
                try:
                    image_path = os.path.join(self.input_dir, filename)
                    image = cv2.imread(image_path)
                    
                    if image is None:
                        print(f"Erro ao carregar: {filename}")
                        continue
                    
                    self.process_image(image, filename)
                    
                except Exception as e:
                    print(f"Erro ao processar {filename}: {str(e)}")

def main():
    # Configuração dos diretórios
    datasets = {
        'DRIVE': {
            'training': 'datasets/DRIVE/training/images',
            'test': 'datasets/DRIVE/test/images'
        },
        'STARE': 'datasets/stare-dataset'
    }
    
    output_dir = 'resultados/segmentacao'
    
    # Processa cada dataset
    for dataset_name, paths in datasets.items():
        print(f"\nProcessando dataset: {dataset_name}")
        
        if isinstance(paths, dict):
            # Para DRIVE (tem subdiretórios)
            for subset, path in paths.items():
                print(f"Processando subset: {subset}")
                processor = RetinalVesselSegmentation(path, f"{output_dir}/{dataset_name}/{subset}")
                processor.process_dataset()
        else:
            # Para STARE (sem subdiretórios)
            processor = RetinalVesselSegmentation(paths, f"{output_dir}/{dataset_name}")
            processor.process_dataset()

if __name__ == "__main__":
    main()
