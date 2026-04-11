import json
import os
from http.server import BaseHTTPRequestHandler


PROMPT_TEMPLATE = """Você é especialista em marketing digital para capacitações profissionais do setor público (SUAS — Sistema Único de Assistência Social).

Com base nas informações abaixo, escreva uma legenda completa e persuasiva para anúncio no Instagram/Facebook:

CAPACITAÇÃO: {nome}
DATA: {data}
LOCAL: {local}

Estruture a legenda assim:
1. Abertura impactante (1-2 linhas que gerem curiosidade ou urgência)
2. O que será aprendido e para quem é indicado (3-4 linhas)
3. Data e local formatados com emojis 📅 e 📍
4. Call to action direto (WhatsApp / garantir vaga)
5. 6-8 hashtags relevantes

Tom: profissional, motivador, acessível.
Público-alvo: trabalhadores e gestores do SUAS, assistentes sociais, psicólogos, coordenadores de CRAS/CREAS.
Escreva apenas a legenda, sem títulos ou comentários extras."""


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            self._json(500, {"erro": "ANTHROPIC_API_KEY não configurada nas variáveis do Vercel"})
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            cap = json.loads(self.rfile.read(length))

            import anthropic
            client = anthropic.Anthropic(api_key=api_key)

            prompt = PROMPT_TEMPLATE.format(
                nome=cap.get("nome", ""),
                data=cap.get("data", ""),
                local=cap.get("local", ""),
            )

            msg = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            self._json(200, {"texto": msg.content[0].text.strip()})

        except Exception as exc:
            self._json(500, {"erro": str(exc)})

    def _json(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
