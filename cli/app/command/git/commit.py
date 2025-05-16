import click
import subprocess
import re
import uuid
from pathlib import Path

from openai import OpenAI

DEFAULT_MODEL = "o3-2025-04-16"

@click.command(name="commit")
@click.option("--dry-run", is_flag=True, help="Mostrar a mensagem de commit sem executar o commit")
@click.option("--verbose", is_flag=True, help="Exibir comandos git e suas saídas")
def commit(dry_run, verbose):
    """Gera um commit convencional em português baseado nas alterações em stage."""
    # Verificar se existem mudanças em stage
    if not _has_staged_changes(verbose):
        click.secho("Não há alterações em stage para commit", fg="red")
        return

    # Obter informações das alterações em stage
    staged_changes = _get_staged_changes(verbose)

    click.secho("Gerando mensagem de commit...", fg="green")
    commit_message = _generate_commit_message(staged_changes)

    click.secho(f"Mensagem de commit gerada: {commit_message}", fg="yellow")

    if dry_run:
        click.secho(f'Modo dry run ativado. Comando que seria executado: git commit -m "{commit_message}"', fg="green")
        return

    # Executar o commit
    if verbose:
        click.secho(f'Executando: git commit -m "{commit_message}"', fg="blue")

    try:
        subprocess.check_output(["git", "commit", "-m", commit_message])
        click.secho("Commit realizado com sucesso!", fg="green")
    except subprocess.CalledProcessError as e:
        click.secho(f"Erro ao executar commit: {str(e)}", fg="red")


def _has_staged_changes(verbose=False):
    """Verifica se existem alterações em stage."""
    if verbose:
        click.secho("Executando: git diff --staged --quiet || echo 'has changes'", fg="blue")

    try:
        # Se retornar status 0, não há alterações (diff não encontrou diferenças)
        subprocess.check_call(["git", "diff", "--staged", "--quiet"])
        return False
    except subprocess.CalledProcessError:
        # Status diferente de 0 indica que há alterações
        return True


def _get_staged_changes(verbose=False):
    """Obtém as alterações em stage."""
    # Obter nomes dos arquivos alterados
    if verbose:
        click.secho("Executando: git diff --staged --name-only", fg="blue")

    staged_files = subprocess.check_output(["git", "diff", "--staged", "--name-only"]).decode().strip().split("\n")
    if verbose:
        click.secho(f"Arquivos em stage: {staged_files}", fg="blue")

    # Obter o diff completo
    if verbose:
        click.secho("Executando: git diff --staged", fg="blue")

    diff_content = subprocess.check_output(["git", "diff", "--staged"]).decode(errors='replace').strip()
    if verbose:
        click.secho(f"Conteúdo do diff:\n{diff_content}", fg="blue")

    return {
        "files": staged_files,
        "diff": diff_content
    }


def _generate_commit_message(staged_changes):
    """Gera uma mensagem de commit convencional em português brasileiro usando OpenAI."""
    prompt = COMMIT_PROMPT_TMPL.format(
        files="\n".join(staged_changes["files"]),
        diff=staged_changes["diff"]
    )

    # Salvar o prompt em um arquivo temporário para debug
    tmp_file = Path(f"/tmp/commit_prompt_{uuid.uuid4()}.txt")
    tmp_file.write_text(prompt)
    click.secho(f"Prompt salvo em {tmp_file}", fg="green")

    # Gerar a mensagem de commit
    response = (
        OpenAI()
        .chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        .choices[0]
        .message.content
    )

    # Extrair a mensagem de commit do formato MENSAGEM: resposta
    message_match = re.search(r"MENSAGEM:\s*(.*?)(?:\n|$)", response)

    if not message_match:
        click.secho("Falha ao processar resposta da IA", fg="red")
        click.secho(f"Resposta completa:\n{response}", fg="red")
        return "chore: alterações no projeto"

    return message_match.group(1).strip()


COMMIT_PROMPT_TMPL = """
<arquivos_alterados>
{files}
</arquivos_alterados>

<diff_alteracoes>
{diff}
</diff_alteracoes>

<exemplos>
Exemplo 1:
MENSAGEM: feat: implementada autenticação de usuários

Exemplo 2:
MENSAGEM: fix: corrigido vazamento de memória no worker

Exemplo 3:
MENSAGEM: chore: atualização de dependências

Exemplo 4:
MENSAGEM: docs: atualizadas instruções de instalação

Exemplo 5:
MENSAGEM: refactor: simplificado sistema de cache

Exemplo 6:
MENSAGEM: test: adicionados testes para API de pagamentos

Exemplo 7:
MENSAGEM: style: formatação do código conforme padrão
</exemplos>

Você é um gerador de mensagens de commit no estilo Conventional Commits. Siga estas regras:

1. Use sempre o idioma português brasileiro
2. Escolha um dos prefixos: feat, fix, chore, docs, refactor, test, style
3. A mensagem deve ser concisa (máximo 50 caracteres)
4. Use linguagem simples e direta
5. Não use adjetivos desnecessários
6. Comece com verbos no particípio (implementado, corrigido, etc.)
7. Não use sinais de pontuação no final da mensagem

Com base nas alterações em stage, gere uma mensagem de commit que siga o formato:
MENSAGEM: <prefixo>: <descrição concisa em português>
"""
