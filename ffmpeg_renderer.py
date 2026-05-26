"""
ffmpeg_renderer.py
Renderização programática de vídeo via FFmpeg — cortes temporais e overlays
de texto em timeline, sem depender de suites de edição com interface gráfica.
"""
import os
import shutil
import subprocess
from pathlib import Path


class FFmpegRenderer:
    """Renderizador via FFmpeg para automatizar cortes e overlays em pipeline."""

    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()

    def _find_ffmpeg(self):
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"], capture_output=True, timeout=5
            )
            if result.returncode == 0:
                return "ffmpeg"
        except FileNotFoundError:
            pass

        common = [
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
            "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
            os.path.expanduser("~\\ffmpeg\\bin\\ffmpeg.exe"),
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
        ]
        for p in common:
            if os.path.isfile(p):
                return p
        return None

    def disponivel(self) -> bool:
        return self.ffmpeg_path is not None

    def renderizar(self, input_path: str, cortes: list, overlays: list,
                   output_dir: str, job_id: str = "01") -> str:
        """
        Pipeline: cortes temporais + overlays de texto.

        Args:
            input_path:  Caminho do vídeo bruto.
            cortes:      Lista de dicts com {'timestamp': float} para cortar.
            overlays:    Lista de dicts com {'titulo': str, 'conteudo': str}.
            output_dir:  Pasta de saída.
            job_id:      Identificador do trabalho.
        Returns:
            Caminho do vídeo final renderizado.
        """
        if not self.disponivel():
            return self._fallback_copy(input_path, output_dir, job_id)

        print(f"[FFmpeg] Renderizando: {input_path}")

        video_cortado = self._aplicar_cortes(input_path, cortes, output_dir, job_id)
        video_final   = self._aplicar_overlays(video_cortado, overlays, output_dir, job_id)
        return video_final

    # ── Internos ────────────────────────────────────────────────

    def _aplicar_cortes(self, input_path, cortes, output_dir, job_id):
        if not cortes:
            return input_path

        cortes = sorted(cortes, key=lambda x: x["timestamp"])
        segs = []
        ultimo = 0.0
        for c in cortes:
            t = c["timestamp"]
            if t - ultimo > 0.5:
                segs.append(f"between(t,{ultimo},{t})")
            ultimo = t
        segs.append(f"between(t,{ultimo},1000000)")

        sel = "select='" + "+".join(segs) + "'"
        out = os.path.join(output_dir, f"cortado_{job_id}.mp4")

        cmd = [
            self.ffmpeg_path, "-i", input_path,
            "-vf", f"{sel},setpts=N/FRAME_RATE/TB",
            "-af", f"aselect='{sel}',asetpts=N/SR/TB",
            "-c:v", "libx264", "-c:a", "aac", "-preset", "fast", "-y", out,
        ]
        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            print(f"  ✓ Cortes aplicados: {len(cortes)} pontos")
            return out
        except Exception as e:
            print(f"  ✗ Erro nos cortes: {e}")
            return input_path

    def _aplicar_overlays(self, input_path, overlays, output_dir, job_id):
        out = os.path.join(output_dir, f"render_{job_id}.mp4")
        filtros = []

        # Titulo nos primeiros 3 segundos
        titulo = overlays[0].get("titulo", "Video")[:50] if overlays else "Video"
        filtros.append(
            f"drawtext=text='{titulo}':fontcolor=white:fontsize=24:"
            f"x=(w-text_w)/2:y=h-text_h-20:enable='between(t,0,3)'"
        )

        # Overlays sequenciais
        t_atual = 3.0
        for info in overlays:
            ti = info.get("titulo", "Info")[:30]
            tx = info.get("conteudo", "")[:50]
            filtros.append(
                f"drawtext=text='{ti}':fontcolor=orange:fontsize=18:"
                f"x=w-text_w-20:y=20:enable='between(t,{t_atual},{t_atual+3})'"
            )
            filtros.append(
                f"drawtext=text='{tx}':fontcolor=white:fontsize=14:"
                f"x=w-text_w-20:y=50:enable='between(t,{t_atual},{t_atual+3})'"
            )
            t_atual += 3.0

        if not filtros:
            shutil.copy2(input_path, out)
            return out

        cmd = [
            self.ffmpeg_path, "-i", input_path,
            "-vf", ",".join(filtros),
            "-c:v", "libx264", "-c:a", "copy",
            "-preset", "fast", "-y", out,
        ]
        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            print(f"  ✓ Overlays aplicados: {len(overlays)} blocos")
            return out
        except Exception as e:
            print(f"  ✗ Erro nos overlays: {e}")
            return input_path

    def _fallback_copy(self, input_path, output_dir, job_id):
        out = os.path.join(output_dir, f"copia_{job_id}.mp4")
        try:
            shutil.copy2(input_path, out)
            print("⚠ FFmpeg nao encontrado — copia feita sem processamento.")
            return out
        except Exception:
            return input_path


if __name__ == "__main__":
    r = FFmpegRenderer()
    if not r.disponivel():
        print("FFmpeg nao encontrado no PATH.")
        exit(1)

    # Demo: corta em 5s e 12s, adiciona 2 overlays
    demo = r.renderizar(
        "input.mp4",
        cortes=[{"timestamp": 5.0}, {"timestamp": 12.0}],
        overlays=[
            {"titulo": "Capitulo 1", "conteudo": "Introducao ao tema"},
            {"titulo": "Capitulo 2", "conteudo": "Dados da pesquisa"},
        ],
        output_dir="./output",
        job_id="demo01",
    )
    print(f"Final: {demo}")
