import click
from datetime import datetime, timedelta
from typing import List, Dict
from openai import OpenAI

from cli.app.command.notes.utils import list_items


@click.command()
@click.option("--days", type=int, default=1, help="Number of days to summarize (default: 1)")
@click.option("--verbose", is_flag=True, help="Show verbose output")
def summary(days: int, verbose: bool):
    """Summarize notes and completed tasks from the last N days."""
    # Validate input
    if days <= 0:
        click.echo("Error: Number of days must be greater than zero.")
        return

    # Calculate the cutoff date
    today = datetime.now()
    cutoff_date = today - timedelta(days=days)

    if verbose:
        click.echo(f"Summarizing items since: {cutoff_date.strftime('%Y-%m-%d')}")

    try:
        # Get all items
        all_items = list_items()

        # Categories for our summary
        completed_tasks = []    # Tasks completed within the timeframe
        recent_pending_tasks = []  # Recently created pending tasks
        older_pending_tasks = []   # Older pending tasks still incomplete
        recent_notes = []          # Notes created within the timeframe

        for item in all_items:
            try:
                created_at = datetime.fromisoformat(item["created_at"])

                # Process tasks
                if item["type"] == "task":
                    is_completed = item.get("completed_at") is not None

                    if is_completed:
                        # Check if completed within timeframe
                        completed_at = datetime.fromisoformat(item["completed_at"])
                        if completed_at >= cutoff_date:
                            completed_tasks.append(item)
                    else:  # Pending tasks
                        if created_at >= cutoff_date:
                            recent_pending_tasks.append(item)
                        else:
                            older_pending_tasks.append(item)

                # Process notes
                elif item["type"] == "note" and created_at >= cutoff_date:
                    recent_notes.append(item)

            except (KeyError, ValueError) as e:
                if verbose:
                    click.echo(f"Warning: Skipping item due to error: {e}")
                continue

        if not (completed_tasks or recent_pending_tasks or older_pending_tasks or recent_notes):
            click.echo(f"No notes or tasks found for the last {days} day(s).")
            return

        # Prepare the content for the OpenAI prompt with clear sections
        content = _prepare_content(completed_tasks, recent_pending_tasks, older_pending_tasks, recent_notes)

        if verbose:
            click.echo("Generating summary...")

        # Generate the summary using OpenAI
        summary_text = _generate_summary(content, days)

        # Display the summary
        click.echo("\n" + "=" * 50)
        click.echo(f"RESUMO DOS ÚLTIMOS {days} DIA(S)")
        click.echo("=" * 50 + "\n")
        click.echo(summary_text)

    except Exception as e:
        click.echo(f"Erro ao gerar resumo: {str(e)}")
        if verbose:
            import traceback
            click.echo(traceback.format_exc())


def _prepare_content(completed_tasks: List[Dict], recent_pending_tasks: List[Dict],
                     older_pending_tasks: List[Dict], recent_notes: List[Dict]) -> str:
    """Prepare the content for the OpenAI prompt with clear sections."""
    content_parts = []

    # 1. Section for completed tasks
    if completed_tasks:
        content_parts.append("## TAREFAS CONCLUÍDAS:")
        for task in completed_tasks:
            created_at = datetime.fromisoformat(task["created_at"]).strftime("%Y-%m-%d %H:%M")
            completed_at = datetime.fromisoformat(task["completed_at"]).strftime("%Y-%m-%d %H:%M")

            # Handle None values for content
            task_content = task.get("content", "") or ""
            task_content = task_content.strip()
            tags = ", ".join(task.get("tags", []) or [])

            # Use content preview as display text (first line or first 50 chars)
            content_preview = task_content.split('\n')[0][:50]
            if len(task_content.split('\n')[0]) > 50:
                content_preview += "..."

            task_text = f"- Tarefa: {content_preview} (Criada: {created_at}, Concluída: {completed_at})"
            if tags:
                task_text += f" [Tags: {tags}]"
            if task_content:
                # Limit content length and format for readability
                task_text += f"\n  Detalhes: {task_content[:500]}"
                if len(task_content) > 500:
                    task_text += "..."

            content_parts.append(task_text)

    # 2.1 Section for recent pending tasks
    if recent_pending_tasks:
        content_parts.append("\n## TAREFAS PENDENTES RECENTES:")
        for task in recent_pending_tasks:
            created_at = datetime.fromisoformat(task["created_at"]).strftime("%Y-%m-%d %H:%M")

            task_content = task.get("content", "") or ""
            task_content = task_content.strip()
            tags = ", ".join(task.get("tags", []) or [])

            # Use content preview as display text
            content_preview = task_content.split('\n')[0][:50]
            if len(task_content.split('\n')[0]) > 50:
                content_preview += "..."

            task_text = f"- Tarefa: {content_preview} (Criada: {created_at})"
            if tags:
                task_text += f" [Tags: {tags}]"
            if task_content:
                task_text += f"\n  Detalhes: {task_content[:500]}"
                if len(task_content) > 500:
                    task_text += "..."

            content_parts.append(task_text)

    # 2.2 Section for older pending tasks
    if older_pending_tasks:
        content_parts.append("\n## TAREFAS PENDENTES ANTIGAS:")
        for task in older_pending_tasks:
            created_at = datetime.fromisoformat(task["created_at"]).strftime("%Y-%m-%d %H:%M")

            task_content = task.get("content", "") or ""
            task_content = task_content.strip()
            tags = ", ".join(task.get("tags", []) or [])

            # Use content preview as display text
            content_preview = task_content.split('\n')[0][:50]
            if len(task_content.split('\n')[0]) > 50:
                content_preview += "..."

            task_text = f"- Tarefa: {content_preview} (Criada: {created_at})"
            if tags:
                task_text += f" [Tags: {tags}]"
            if task_content:
                task_text += f"\n  Detalhes: {task_content[:500]}"
                if len(task_content) > 500:
                    task_text += "..."

            content_parts.append(task_text)

    # 3. Section for recent notes
    if recent_notes:
        content_parts.append("\n## NOTAS RECENTES:")
        for note in recent_notes:
            created_at = datetime.fromisoformat(note["created_at"]).strftime("%Y-%m-%d %H:%M")

            note_content = note.get("content", "") or ""
            note_content = note_content.strip()
            tags = ", ".join(note.get("tags", []) or [])

            # Use content preview as display text
            content_preview = note_content.split('\n')[0][:50]
            if len(note_content.split('\n')[0]) > 50:
                content_preview += "..."

            note_text = f"- Nota: {content_preview} (Criada: {created_at})"
            if tags:
                note_text += f" [Tags: {tags}]"
            if note_content:
                note_text += f"\n  Conteúdo: {note_content[:500]}"
                if len(note_content) > 500:
                    note_text += "..."

            content_parts.append(note_text)

    return "\n".join(content_parts)


def _generate_summary(content: str, days: int) -> str:
    """Generate a summary using OpenAI's API."""
    try:
        client = OpenAI()

        time_period = "do dia de ontem" if days == 1 else f"dos últimos {days} dias"

        # Crafting a clear system message
        system_message = """
        Você é um assistente especializado em resumir notas e tarefas.
        Seu trabalho é criar um resumo conciso, claro e bem organizado de notas e tarefas.
        """

        # Crafting a clear user prompt with instructions
        user_prompt = f"""
        # Resumo {time_period}

        Por favor, analise as seguintes notas e tarefas e crie um resumo executivo que:

        1. Destaque as principais atividades concluídas
        2. Identifique as principais tarefas pendentes que precisam de atenção
        3. Destaque os temas principais nas notas recentes
        4. Identifique quaisquer padrões ou tendências notáveis
        5. Sugira áreas que possam precisar de mais foco ou atenção

        Apresente o resumo em formato Markdown, incluindo seções claras e listas para facilitar a leitura.
        Foque no conteúdo e não apenas nos títulos.

        Aqui estão os dados:

        {content}
        """

        # Making the API call
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error generating summary: {str(e)}"
