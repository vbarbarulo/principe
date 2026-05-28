import os
import sys
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.utils.rotinas_parser import RotinasParser

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

class RoutineScheduler:
    def __init__(self, application):
        self.application = application
        self.scheduler = AsyncIOScheduler()
        self.parser = RotinasParser()

    async def send_reminder(self, rotina_id, titulo, horario, tarefas):
        """
        Dispara uma mensagem ativa no Telegram do usuário cobrando a rotina atual.
        """
        # Substitua pelo ID fixo do chat se quiser forçar o envio a um usuário específico.
        # Por padrão, vamos tentar obter o chat_id ativo do banco ou enviar ao Vini.
        chat_id = 153099903 # ID exemplo do Telegram do usuário (ou use uma variável global/do banco)
        
        tarefas_fmt = "\n".join([f"- [ ] {t['texto']}" for t in tarefas])
        
        msg = (
            f"🎖️ **ALERTA DO SARGENTO: ROTINA GATILHO!** ⏰\n\n"
            f"Está na hora da rotina: **{titulo}** [{horario}]!\n"
            f"Soldado, pare tudo o que está fazendo e execute:\n\n"
            f"{tarefas_fmt}\n\n"
            f"Sem desculpas! Responda me avisando o que concluiu."
        )
        try:
            await self.application.bot.send_message(chat_id=chat_id, text=msg)
            print(f"Lembrete ativo enviado para a rotina: {rotina_id}")
        except Exception as e:
            print(f"Erro ao enviar lembrete ativo para chat_id {chat_id}: {str(e)}")

    def start(self):
        """
        Agenda todas as rotinas encontradas no rotinas.md.
        """
        rotinas = self.parser.parse()
        for rotina_id, info in rotinas.items():
            horario = info["horario"] # Ex: "06:00"
            try:
                hora, minuto = map(int, horario.split(":"))
                
                # Agenda o job diário
                self.scheduler.add_job(
                    self.send_reminder,
                    "cron",
                    hour=hora,
                    minute=minuto,
                    args=[rotina_id, info["titulo"], horario, info["tarefas"]],
                    id=f"job_{rotina_id}",
                    replace_existing=True
                )
                print(f"Agendado com sucesso: {info['titulo']} para {horario}")
            except Exception as e:
                print(f"Falha ao agendar rotina {rotina_id}: {str(e)}")

        self.scheduler.start()
        print("Agendador de rotinas ativo e rodando em segundo plano.")
