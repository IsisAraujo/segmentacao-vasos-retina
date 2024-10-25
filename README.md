# Segmentação de Vasos Sanguíneos da Retina

## Descrição

Este projeto implementa um pipeline de processamento de imagens para segmentar vasos sanguíneos em imagens da retina. Utilizando técnicas avançadas de visão computacional, o código extrai e visualiza a rede vascular da retina, fornecendo uma ferramenta para pesquisadores e profissionais de saúde interessados em entender sobre o diagnóstico assistido por computador de doenças oculares.

## Funcionalidades

- Extração de canais de cor (vermelho, verde, azul)
- Criação de máscara para isolar a região de interesse
- Aplicação de filtro gaussiano para suavização
- Realce de vasos usando operação black-hat
- Limiarização binária usando o método de Otsu
- Reconstrução morfológica para melhorar a segmentação
- Geração de imagens combinadas com todas as etapas do processo

## Requisitos

- Python 3.x
- OpenCV (cv2)
- NumPy
- tqdm

## Instalação

1. Clone este repositório:
   ```
   git clone https://github.com/seu-usuario/segmentacao-vasos-retina.git
   ```

2. Instale as dependências:
   ```
   pip install opencv-python numpy tqdm
   ```

## Uso

1. Organize suas imagens de retina nos diretórios apropriados dentro da pasta `datasets`.

2. Execute o script principal:
   ```
   python extrator_vasos_sanguineos.py
   ```

3. Os resultados serão salvos no diretório `resultados/segmentacao`.

## Estrutura do Projeto

├── datasets/
│   ├── DRIVE/
│   │   ├── training/
│   │   └── test/
│   └── STARE/
├── resultados/
│   └── segmentacao/
├── extrator_vasos_sanguineos.py
└── README.md
