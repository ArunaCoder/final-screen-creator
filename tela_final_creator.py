#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para criar telas finais para vídeos do YouTube.

Este script combina três camadas de vídeo:
1. Um vídeo de fundo (com prefixo específico)
2. Um vídeo intermediário transparente (overlay)
3. Um vídeo específico menor posicionado em um local determinado

Autor: Manus AI
Data: 22/05/2025
"""

import os
import sys
from moviepy.editor import VideoFileClip, CompositeVideoClip


def create_final_screen(background_video_path, specific_video_path, overlay_video_path, output_path, 
                        duration=20, resolution=(1280, 720), 
                        specific_video_width=469, specific_video_position=(733.5, 398.8)):
    """
    Cria uma tela final combinando três camadas de vídeo.
    
    Args:
        background_video_path (str): Caminho para o vídeo de fundo
        specific_video_path (str): Caminho para o vídeo específico menor
        overlay_video_path (str): Caminho para o vídeo de overlay intermediário
        output_path (str): Caminho para salvar o vídeo final
        duration (int): Duração do vídeo final em segundos
        resolution (tuple): Resolução do vídeo final (largura, altura)
        specific_video_width (int): Largura do vídeo específico
        specific_video_position (tuple): Posição (x, y) do vídeo específico
    
    Returns:
        bool: True se o processo foi bem-sucedido, False caso contrário
    """
    try:
        print(f"Processando: {os.path.basename(background_video_path)} + {os.path.basename(specific_video_path)}")
        
        # Carrega os vídeos
        background_clip = VideoFileClip(background_video_path).resize(resolution)
        overlay_clip = VideoFileClip(overlay_video_path).resize(resolution)
        specific_clip = VideoFileClip(specific_video_path)
        
        # Corta os vídeos para a duração especificada
        background_clip = background_clip.subclip(0, duration)
        overlay_clip = overlay_clip.subclip(0, duration)
        
        # Se o vídeo específico for maior que a duração desejada, corta-o
        if specific_clip.duration > duration:
            specific_clip = specific_clip.subclip(0, duration)
        
        # Redimensiona o vídeo específico mantendo a proporção
        original_width = specific_clip.w
        original_height = specific_clip.h
        aspect_ratio = original_height / original_width
        specific_height = int(specific_video_width * aspect_ratio)
        specific_clip = specific_clip.resize(width=specific_video_width)
        
        # Define a posição do vídeo específico
        specific_clip = specific_clip.set_position(specific_video_position)
        
        # Combina os vídeos
        final_clip = CompositeVideoClip([
            background_clip,
            overlay_clip,
            specific_clip
        ], size=resolution)
        
        # Define a duração final
        final_clip = final_clip.set_duration(duration)
        
        # Salva o vídeo final
        final_clip.write_videofile(
            output_path, 
            codec='libx264', 
            audio_codec='aac', 
            fps=30, 
            preset='medium',
            threads=4
        )
        
        # Fecha os clips para liberar recursos
        background_clip.close()
        overlay_clip.close()
        specific_clip.close()
        final_clip.close()
        
        print(f"Vídeo salvo em: {output_path}")
        return True
    
    except Exception as e:
        print(f"Erro ao processar os vídeos: {str(e)}")
        return False


def process_videos(background_folder, specific_folder, overlay_video_path, output_folder,
                  background_prefix="Autoc", duration=20, resolution=(1280, 720),
                  specific_video_width=469, specific_video_position=(733.5, 398.8)):
    """
    Processa todos os vídeos nas pastas especificadas.
    
    Args:
        background_folder (str): Pasta contendo os vídeos de fundo
        specific_folder (str): Pasta contendo os vídeos específicos
        overlay_video_path (str): Caminho para o vídeo de overlay
        output_folder (str): Pasta para salvar os vídeos finais
        background_prefix (str): Prefixo dos vídeos de fundo
        duration (int): Duração do vídeo final em segundos
        resolution (tuple): Resolução do vídeo final (largura, altura)
        specific_video_width (int): Largura do vídeo específico
        specific_video_position (tuple): Posição (x, y) do vídeo específico
    
    Returns:
        int: Número de vídeos processados com sucesso
    """
    # Cria a pasta de saída se não existir
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Pasta de saída criada: {output_folder}")
    
    # Encontra o vídeo de fundo
    background_videos = [f for f in os.listdir(background_folder) 
                        if f.startswith(background_prefix) and 
                        (f.endswith('.mp4') or f.endswith('.avi') or f.endswith('.mov'))]
    
    if not background_videos:
        print(f"Nenhum vídeo de fundo encontrado com o prefixo '{background_prefix}'")
        return 0
    
    # Usa o primeiro vídeo de fundo encontrado
    background_video_path = os.path.join(background_folder, background_videos[0])
    print(f"Usando vídeo de fundo: {background_videos[0]}")
    
    # Encontra os vídeos específicos
    specific_videos = [f for f in os.listdir(specific_folder) 
                      if f.endswith('.mp4') or f.endswith('.avi') or f.endswith('.mov')]
    
    if not specific_videos:
        print("Nenhum vídeo específico encontrado")
        return 0
    
    # Processa cada vídeo específico
    success_count = 0
    for specific_video in specific_videos:
        specific_video_path = os.path.join(specific_folder, specific_video)
        output_path = os.path.join(output_folder, specific_video)
        
        if create_final_screen(
            background_video_path, 
            specific_video_path, 
            overlay_video_path, 
            output_path,
            duration,
            resolution,
            specific_video_width,
            specific_video_position
        ):
            success_count += 1
    
    return success_count


def main():
    """Função principal do script."""
    # Diretório atual onde o script está sendo executado
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define os caminhos padrão relativos ao diretório do script
    background_folder = os.path.join(script_dir, "background")
    specific_folder = os.path.join(script_dir, "cortes")
    output_folder = os.path.join(script_dir, "output")
    
    # Procura pelo arquivo de overlay no diretório do script
    overlay_files = [f for f in os.listdir(script_dir) 
                    if f.startswith("Overlay Tela Final") and 
                    (f.endswith('.mp4') or f.endswith('.avi') or f.endswith('.mov'))]
    
    if not overlay_files:
        print("Erro: Arquivo de overlay não encontrado no diretório do script.")
        print("O arquivo deve começar com 'Overlay Tela Final' e ter extensão .mp4, .avi ou .mov")
        return 1
    
    overlay_video_path = os.path.join(script_dir, overlay_files[0])
    
    # Verifica se as pastas existem
    if not os.path.exists(background_folder):
        print(f"Erro: Pasta de vídeos de fundo não encontrada: {background_folder}")
        print("Por favor, crie uma pasta chamada 'background' no mesmo diretório do script.")
        return 1
    
    if not os.path.exists(specific_folder):
        print(f"Erro: Pasta de vídeos específicos não encontrada: {specific_folder}")
        print("Por favor, crie uma pasta chamada 'cortes' no mesmo diretório do script.")
        return 1
    
    print("\n=== Configuração ===")
    print(f"Pasta de vídeos de fundo: {background_folder}")
    print(f"Pasta de vídeos específicos: {specific_folder}")
    print(f"Vídeo de overlay: {overlay_video_path}")
    print(f"Pasta de saída: {output_folder}")
    print("===================\n")
    
    # Processa os vídeos
    success_count = process_videos(
        background_folder,
        specific_folder,
        overlay_video_path,
        output_folder,
        "Autoc",  # Prefixo padrão para vídeos de fundo
        20,       # Duração padrão de 20 segundos
        (1280, 720),  # Resolução padrão
        469,      # Largura do vídeo específico
        (733.5, 398.8)  # Posição do vídeo específico
    )
    
    print(f"\nProcessamento concluído. {success_count} vídeos processados com sucesso.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
