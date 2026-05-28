import subprocess
import os

class GitUtils:
    def __init__(self, repo_path=None):
        if repo_path is None:
            # Padrão: diretório raiz do projeto
            self.repo_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        else:
            self.repo_path = repo_path

    def _run_git_cmd(self, args):
        """Executa um comando git e retorna (success, stdout, stderr)"""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False
            )
            success = result.returncode == 0
            return success, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return False, "", str(e)

    def is_git_repo(self):
        """Verifica se o diretório é um repositório git"""
        success, _, _ = self._run_git_cmd(["status"])
        return success

    def init_repo(self):
        """Inicializa um repositório git se não existir"""
        return self._run_git_cmd(["init"])

    def get_current_branch(self):
        """Retorna o nome da branch atual"""
        success, stdout, _ = self._run_git_cmd(["branch", "--show-current"])
        if success and stdout:
            return stdout
        # Fallback para versões antigas de git
        success, stdout, _ = self._run_git_cmd(["rev-parse", "--abbrev-ref", "HEAD"])
        return stdout if success else "master"

    def checkout_branch(self, branch_name):
        """Muda para uma branch existente"""
        return self._run_git_cmd(["checkout", branch_name])

    def create_and_checkout_branch(self, branch_name, base_branch="master"):
        """Cria e muda para uma nova branch baseada em outra"""
        # Garante que estamos na base_branch primeiro
        self.checkout_branch(base_branch)
        # Cria a nova branch
        success, stdout, stderr = self._run_git_cmd(["checkout", "-b", branch_name])
        # Se falhar porque a branch já existe, apenas faz checkout nela
        if not success and "already exists" in stderr:
            return self.checkout_branch(branch_name)
        return success, stdout, stderr

    def add_all_and_commit(self, message):
        """Executa git add . e git commit -m <message>"""
        # Adiciona tudo
        add_success, _, add_err = self._run_git_cmd(["add", "."])
        if not add_success:
            return False, "", f"Erro no git add: {add_err}"
        
        # Commita
        commit_success, stdout, commit_err = self._run_git_cmd(["commit", "-m", message])
        # Ignora se não houver modificações para commitar
        if not commit_success and "nothing to commit" in commit_err:
            return True, "Nada para commitar", ""
        return commit_success, stdout, commit_err

    def merge_branch(self, source_branch, target_branch="master"):
        """Mescla a source_branch na target_branch"""
        # Muda para a branch destino
        checkout_success, _, checkout_err = self.checkout_branch(target_branch)
        if not checkout_success:
            return False, "", f"Erro ao ir para a branch destino {target_branch}: {checkout_err}"

        # Realiza a mesclagem
        merge_success, stdout, merge_err = self._run_git_cmd(["merge", source_branch, "--no-edit"])
        return merge_success, stdout, merge_err
