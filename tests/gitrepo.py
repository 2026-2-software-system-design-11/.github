"""테스트용 임시 git 저장소."""
import subprocess


class Repo:
    def __init__(self, path):
        self.path = path
        self.git("init", "-q", "-b", "develop")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "test")
        self.git("config", "commit.gpgsign", "false")

    def git(self, *args):
        result = subprocess.run(["git", *args], cwd=self.path, check=True, capture_output=True, text=True)
        return result.stdout.strip()

    def write(self, name, lines):
        target = self.path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("".join(f"line {i}\n" for i in range(lines)), encoding="utf-8")

    def commit(self, message, files):
        """files: {경로: 줄 수}. 커밋 sha를 돌려준다."""
        for name, lines in files.items():
            self.write(name, lines)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD")
