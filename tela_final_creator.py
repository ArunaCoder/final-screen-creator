#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para criar telas finais para vídeos do YouTube.

Este script combina três camadas de vídeo:
1. Um vídeo de fundo (com nome baseado na parte inicial do vídeo específico)
2. Um vídeo intermediário transparente (overlay)
3. Um vídeo específico menor posicionado em um local determinado

Autor: Manus AI
Data: 22/05/2025 (modificado em 23/05/2025)
"""

import os
import sys
import re
# from moviepy import VideoFileClip, CompositeVideoClip
from moviepy import *
from moviepy.video.fx.MaskColor import MaskColor


def extrair_prefixo(texto):
    """
    Extrai o prefixo alfabético de um nome de arquivo.
    Exemplo: "Autoc20.mp4" → "Autoc"
    """
    nome = os.path.splitext(os.path.basename(texto))[0]
    match = re.match(r"[^\d]+", nome)
    return match.group(0) if match else None


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
        # background_clip = VideoFileClip(background_video_path).Resize(resolution)
        background_clip = VideoFileClip(background_video_path).with_effects([vfx.Resize(resolution)])
        overlay_clip = VideoFileClip(overlay_video_path).with_effects([vfx.Resize(resolution)])

        specific_clip = VideoFileClip(specific_video_path)

        # Corta os vídeos para a duração especificada
        background_clip = background_clip.subclipped(0, min(duration, background_clip.duration))

        overlay_clip = overlay_clip.subclipped(0, min(duration, overlay_clip.duration))

        effect = MaskColor(color=(0, 0, 0), threshold=10, stiffness=1)
        overlay_clip = effect.apply(overlay_clip)


        if specific_clip.duration > duration:
            specific_clip = specific_clip.subclipped(0, min(duration, specific_clip.duration))

        # Redimensiona o vídeo específico mantendo proporção
        aspect_ratio = specific_clip.h / specific_clip.w
        specific_clip = specific_clip.with_effects([vfx.Resize(width=specific_video_width)])


        # Define a posição
        specific_clip = specific_clip.with_position(specific_video_position)


        # Combina os vídeos
        final_clip = CompositeVideoClip([
            background_clip,
            overlay_clip,
            specific_clip
        ], size=resolution).with_duration(duration)

        # Salva o resultado
        final_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=30,
            preset='medium',
            threads=4
        )

        # Fecha os objetos para liberar memória
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
                  duration=20, resolution=(1280, 720),
                  specific_video_width=469, specific_video_position=(733.5, 398.8)):
    """
    Processa todos os vídeos nas pastas especificadas, associando o vídeo de fundo pelo prefixo textual.

    Args:
        background_folder (str): Pasta contendo os vídeos de fundo
        specific_folder (str): Pasta contendo os vídeos específicos
        overlay_video_path (str): Caminho para o vídeo de overlay
        output_folder (str): Pasta para salvar os vídeos finais
        duration (int): Duração do vídeo final em segundos
        resolution (tuple): Resolução do vídeo final (largura, altura)
        specific_video_width (int): Largura do vídeo específico
        specific_video_position (tuple): Posição (x, y) do vídeo específico

    Returns:
        int: Número de vídeos processados com sucesso
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Pasta de saída criada: {output_folder}")

    SUPPORTED_EXT = ('.mp4', '.avi', '.mov')

    background_videos = [f for f in os.listdir(background_folder)
                         if f.lower().endswith(SUPPORTED_EXT)]

    specific_videos = [f for f in os.listdir(specific_folder)
                       if f.lower().endswith(SUPPORTED_EXT)]

    if not specific_videos:
        print("Nenhum vídeo específico encontrado.")
        return 0

    success_count = 0
    for specific_video in specific_videos:
        prefixo = extrair_prefixo(specific_video)
        if not prefixo:
            print(f"Não foi possível extrair prefixo de {specific_video}. Pulando.")
            continue

        matching_backgrounds = [f for f in background_videos if f.startswith(prefixo)]
        if not matching_backgrounds:
            print(f"Nenhum vídeo de fundo encontrado para o prefixo '{prefixo}'")
            continue

        background_video_path = os.path.join(background_folder, matching_backgrounds[0])
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
    script_dir = os.path.dirname(os.path.abspath(__file__))

    background_folder = os.path.join(script_dir, "background")
    specific_folder = os.path.join(script_dir, "cortes")
    output_folder = os.path.join(script_dir, "output")

    overlay_files = [f for f in os.listdir(script_dir)
                     if f.startswith("Overlay Tela Final") and
                     f.lower().endswith(('.mp4', '.avi', '.mov'))]

    if not overlay_files:
        print("Erro: Arquivo de overlay não encontrado no diretório do script.")
        return 1

    overlay_video_path = os.path.join(script_dir, overlay_files[0])

    if not os.path.exists(background_folder):
        print(f"Erro: Pasta de vídeos de fundo não encontrada: {background_folder}")
        return 1

    if not os.path.exists(specific_folder):
        print(f"Erro: Pasta de vídeos específicos não encontrada: {specific_folder}")
        return 1

    print("\n=== Configuração ===")
    print(f"Pasta de vídeos de fundo: {background_folder}")
    print(f"Pasta de vídeos específicos: {specific_folder}")
    print(f"Vídeo de overlay: {overlay_video_path}")
    print(f"Pasta de saída: {output_folder}")
    print("===================\n")

    success_count = process_videos(
        background_folder,
        specific_folder,
        overlay_video_path,
        output_folder,
        duration=20,
        resolution=(1280, 720),
        specific_video_width=469,
        specific_video_position=(733.5, 398.8)
    )

    print(f"\nProcessamento concluído. {success_count} vídeos processados com sucesso.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
