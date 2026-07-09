import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DockerDemoTest(unittest.TestCase):
    def test_dockerfile_runs_verify_by_default(self):
        dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

        self.assertIn("FROM python:3.11-slim", dockerfile)
        self.assertIn("apt-get install -y --no-install-recommends make", dockerfile)
        self.assertIn('CMD ["make", "verify"]', dockerfile)
        self.assertIn("COPY reports ./reports", dockerfile)
        self.assertIn("COPY probes ./probes", dockerfile)

    def test_makefile_has_containerized_reviewer_demo(self):
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

        self.assertIn("DOCKER_IMAGE ?= ko-evidence-bench:local", makefile)
        self.assertIn("docker-build:", makefile)
        self.assertIn("docker-demo:", makefile)
        self.assertIn("docker run --rm $(DOCKER_IMAGE)", makefile)
        self.assertIn("reproduce-layer-attribution", makefile)
        self.assertIn("check-probe-privacy", makefile)
        self.assertIn("check-qualitative-gallery", makefile)
        self.assertIn("check-system-matrix-report", makefile)
        self.assertIn("check-public-safety", makefile)

    def test_public_docs_explain_docker_demo(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        demo = (ROOT / "reports" / "reviewer_demo.md").read_text(encoding="utf-8")

        self.assertIn("make docker-demo", readme)
        self.assertIn("Containerized demo", readme)
        self.assertIn("make docker-demo", demo)
        self.assertIn("Containerized review path", demo)


if __name__ == "__main__":
    unittest.main()
