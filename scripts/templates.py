#!/usr/bin/env python3
"""
Experiment Templates and Marketplace
Manages reusable chaos experiment templates
"""

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from utils import get_config, get_logger, validate_experiment_name

logger = get_logger(__name__)
config = get_config()


@dataclass
class ExperimentTemplate:
    """Chaos experiment template"""

    name: str
    description: str
    category: str
    phase: str
    parameters: Dict[str, Any]
    template_yaml: str
    author: Optional[str] = None
    version: str = "1.0.0"
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class TemplateManager:
    """Manages experiment templates"""

    def __init__(self):
        self.config = config
        self.templates_dir = Path("templates")
        self.templates_dir.mkdir(exist_ok=True)
        self.marketplace_dir = self.templates_dir / "marketplace"
        self.marketplace_dir.mkdir(exist_ok=True)

    def create_template(
        self,
        name: str,
        description: str,
        category: str,
        phase: str,
        template_yaml: str,
        parameters: Optional[Dict[str, Any]] = None,
        author: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        """Create a new experiment template"""
        try:
            name = validate_experiment_name(name)
        except ValueError as e:
            logger.error(f"Invalid template name: {e}")
            return False

        template = ExperimentTemplate(
            name=name,
            description=description,
            category=category,
            phase=phase,
            parameters=parameters or {},
            template_yaml=template_yaml,
            author=author,
            tags=tags or [],
        )

        # Save template
        template_file = self.templates_dir / f"{name}.yaml"
        template_data = asdict(template)

        try:
            with open(template_file, "w") as f:
                yaml.dump(template_data, f, default_flow_style=False)
            logger.info(f"✅ Created template: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to save template: {e}")
            return False

    def list_templates(
        self, category: Optional[str] = None, phase: Optional[str] = None
    ) -> List[ExperimentTemplate]:
        """List available templates"""
        templates = []

        for template_file in self.templates_dir.glob("*.yaml"):
            try:
                with open(template_file, "r") as f:
                    data = yaml.safe_load(f)
                    template = ExperimentTemplate(**data)

                    # Filter by category and phase
                    if category and template.category != category:
                        continue
                    if phase and template.phase != phase:
                        continue

                    templates.append(template)
            except Exception as e:
                logger.warning(f"Failed to load template {template_file}: {e}")

        return templates

    def get_template(self, name: str) -> Optional[ExperimentTemplate]:
        """Get a specific template"""
        template_file = self.templates_dir / f"{name}.yaml"

        if not template_file.exists():
            return None

        try:
            with open(template_file, "r") as f:
                data = yaml.safe_load(f)
                return ExperimentTemplate(**data)
        except Exception as e:
            logger.error(f"Failed to load template: {e}")
            return None

    def generate_experiment(
        self,
        template_name: str,
        experiment_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
    ) -> Optional[str]:
        """Generate an experiment from a template"""
        template = self.get_template(template_name)
        if not template:
            logger.error(f"Template not found: {template_name}")
            return None

        # Validate experiment name
        try:
            experiment_name = validate_experiment_name(experiment_name)
        except ValueError as e:
            logger.error(f"Invalid experiment name: {e}")
            return None

        # Merge template parameters with provided parameters
        final_parameters = {**template.parameters, **(parameters or {})}

        # Load template YAML
        try:
            template_data = yaml.safe_load(template.template_yaml)
        except Exception as e:
            logger.error(f"Failed to parse template YAML: {e}")
            return None

        # Replace placeholders
        experiment_yaml = self._replace_placeholders(
            template_data,
            experiment_name=experiment_name,
            namespace=namespace or config.app_namespace,
            parameters=final_parameters,
        )

        # Save generated experiment
        experiment_file = Path(config.experiments_dir) / f"{experiment_name}.yaml"
        try:
            with open(experiment_file, "w") as f:
                yaml.dump(experiment_yaml, f, default_flow_style=False)
            logger.info(f"✅ Generated experiment: {experiment_file}")
            return str(experiment_file)
        except Exception as e:
            logger.error(f"Failed to save experiment: {e}")
            return None

    def _replace_placeholders(
        self,
        data: Any,
        experiment_name: str,
        namespace: str,
        parameters: Dict[str, Any],
    ) -> Any:
        """Recursively replace placeholders in YAML data"""
        if isinstance(data, dict):
            return {
                k: self._replace_placeholders(v, experiment_name, namespace, parameters)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [
                self._replace_placeholders(item, experiment_name, namespace, parameters)
                for item in data
            ]
        elif isinstance(data, str):
            # Replace placeholders
            data = data.replace("{{experiment_name}}", experiment_name)
            data = data.replace("{{namespace}}", namespace)
            for key, value in parameters.items():
                data = data.replace(f"{{{{{key}}}}}", str(value))
            return data
        else:
            return data

    def export_template(self, name: str, export_path: Optional[str] = None) -> bool:
        """Export template to marketplace"""
        template = self.get_template(name)
        if not template:
            logger.error(f"Template not found: {name}")
            return False

        export_path = export_path or (self.marketplace_dir / f"{name}.yaml")

        try:
            with open(export_path, "w") as f:
                yaml.dump(asdict(template), f, default_flow_style=False)
            logger.info(f"✅ Exported template to marketplace: {export_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export template: {e}")
            return False

    def import_template(self, template_path: str) -> bool:
        """Import template from marketplace"""
        template_file = Path(template_path)

        if not template_file.exists():
            logger.error(f"Template file not found: {template_path}")
            return False

        try:
            with open(template_file, "r") as f:
                data = yaml.safe_load(f)
                template = ExperimentTemplate(**data)

            # Save to templates directory
            save_path = self.templates_dir / f"{template.name}.yaml"
            with open(save_path, "w") as f:
                yaml.dump(asdict(template), f, default_flow_style=False)

            logger.info(f"✅ Imported template: {template.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to import template: {e}")
            return False


def main():
    """CLI for template management"""
    import argparse

    parser = argparse.ArgumentParser(description="Chaos Experiment Template Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Create template
    create_parser = subparsers.add_parser("create", help="Create a new template")
    create_parser.add_argument("name", help="Template name")
    create_parser.add_argument("description", help="Template description")
    create_parser.add_argument("category", help="Template category")
    create_parser.add_argument("phase", help="Template phase (phase1, phase2, phase3)")
    create_parser.add_argument(
        "--file", required=True, help="Path to template YAML file"
    )
    create_parser.add_argument("--author", help="Template author")
    create_parser.add_argument("--tags", nargs="+", help="Template tags")

    # List templates
    list_parser = subparsers.add_parser("list", help="List templates")
    list_parser.add_argument("--category", help="Filter by category")
    list_parser.add_argument("--phase", help="Filter by phase")

    # Generate experiment
    gen_parser = subparsers.add_parser(
        "generate", help="Generate experiment from template"
    )
    gen_parser.add_argument("template", help="Template name")
    gen_parser.add_argument("experiment", help="Experiment name")
    gen_parser.add_argument("--namespace", help="Kubernetes namespace")
    gen_parser.add_argument("--params", help="Parameters as JSON string")

    # Export template
    export_parser = subparsers.add_parser(
        "export", help="Export template to marketplace"
    )
    export_parser.add_argument("name", help="Template name")
    export_parser.add_argument("--path", help="Export path")

    # Import template
    import_parser = subparsers.add_parser(
        "import", help="Import template from marketplace"
    )
    import_parser.add_argument("path", help="Template file path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    manager = TemplateManager()

    try:
        if args.command == "create":
            # Read template YAML file
            with open(args.file, "r") as f:
                template_yaml = f.read()

            success = manager.create_template(
                name=args.name,
                description=args.description,
                category=args.category,
                phase=args.phase,
                template_yaml=template_yaml,
                author=getattr(args, "author", None),
                tags=getattr(args, "tags", None),
            )
            sys.exit(0 if success else 1)

        elif args.command == "list":
            templates = manager.list_templates(
                category=getattr(args, "category", None),
                phase=getattr(args, "phase", None),
            )
            if templates:
                logger.info("Available templates:")
                for t in templates:
                    logger.info(
                        f"  - {t.name}: {t.description} ({t.category}, {t.phase})"
                    )
            else:
                logger.info("No templates found")

        elif args.command == "generate":
            params = None
            if hasattr(args, "params") and args.params:
                params = json.loads(args.params)

            result = manager.generate_experiment(
                template_name=args.template,
                experiment_name=args.experiment,
                parameters=params,
                namespace=getattr(args, "namespace", None),
            )
            sys.exit(0 if result else 1)

        elif args.command == "export":
            success = manager.export_template(
                name=args.name, export_path=getattr(args, "path", None)
            )
            sys.exit(0 if success else 1)

        elif args.command == "import":
            success = manager.import_template(args.path)
            sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
