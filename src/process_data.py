"""Main script to process all datasets for TechScope AI agents."""

import argparse
import logging
from pathlib import Path
from typing import List, Optional

from .processors import (
    CompetitiveProcessor,
    MarketingProcessor,
    IPLegalProcessor,
    PolicyProcessor,
    TeamProcessor,
    PitchProcessor,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_all_agents(
    raw_data_dir: Path = Path("data/raw"),
    processed_data_dir: Path = Path("data/processed"),
    agent_filter: Optional[List[str]] = None
) -> dict:
    """
    Process all agent datasets.
    
    Args:
        raw_data_dir: Directory containing raw data
        processed_data_dir: Directory for processed data
        agent_filter: Optional list of agents to process (e.g., ['competitive', 'marketing'])
        
    Returns:
        Dictionary with processing results
    """
    results = {}
    
    # Define processors
    processors = {
        'competitive': (CompetitiveProcessor, raw_data_dir / 'competitive'),
        'marketing': (MarketingProcessor, raw_data_dir / 'marketing'),
        'ip_legal': (IPLegalProcessor, raw_data_dir / 'ip_legal'),
        'policy': (PolicyProcessor, raw_data_dir / 'policy'),
        'team': (TeamProcessor, raw_data_dir / 'team'),
        'pitch': (PitchProcessor, raw_data_dir / 'pitch'),
    }
    
    # Process each agent
    for agent_name, (processor_class, input_dir) in processors.items():
        if agent_filter and agent_name not in agent_filter:
            logger.info(f"Skipping {agent_name} (filtered out)")
            continue
        
        if not input_dir.exists():
            logger.warning(f"Input directory not found: {input_dir}")
            results[agent_name] = {'chunks': 0, 'status': 'skipped', 'reason': 'input_dir_not_found'}
            continue
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing {agent_name} datasets")
        logger.info(f"{'='*60}")
        
        try:
            processor = processor_class(output_dir=processed_data_dir / agent_name)
            chunks = processor.process_dataset(input_dir)
            results[agent_name] = {'chunks': chunks, 'status': 'success'}
            logger.info(f"✓ {agent_name}: {chunks} chunks created")
        except Exception as e:
            logger.error(f"✗ {agent_name}: Error - {e}")
            results[agent_name] = {'chunks': 0, 'status': 'error', 'error': str(e)}
    
    return results


def print_summary(results: dict):
    """Print processing summary."""
    logger.info("\n" + "="*60)
    logger.info("PROCESSING SUMMARY")
    logger.info("="*60)
    
    total_chunks = 0
    successful = 0
    failed = 0
    
    for agent_name, result in results.items():
        status = result['status']
        chunks = result['chunks']
        
        if status == 'success':
            logger.info(f"✓ {agent_name}: {chunks} chunks")
            total_chunks += chunks
            successful += 1
        elif status == 'skipped':
            logger.info(f"⏭️  {agent_name}: Skipped - {result.get('reason', 'unknown')}")
        else:
            logger.error(f"✗ {agent_name}: Failed - {result.get('error', 'unknown error')}")
            failed += 1
    
    logger.info(f"\nTotal chunks: {total_chunks}")
    logger.info(f"Successful: {successful}/{len(results)}")
    logger.info(f"Failed: {failed}/{len(results)}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Process datasets for TechScope AI agents"
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=Path("data/raw"),
        help="Directory containing raw data (default: data/raw)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/processed"),
        help="Directory for processed data (default: data/processed)"
    )
    parser.add_argument(
        "--agents",
        nargs="+",
        choices=['competitive', 'marketing', 'ip_legal', 'policy', 'team', 'pitch'],
        help="Process specific agents only (default: all)"
    )
    
    args = parser.parse_args()
    
    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process datasets
    results = process_all_agents(
        raw_data_dir=args.raw_dir,
        processed_data_dir=args.output_dir,
        agent_filter=args.agents
    )
    
    # Print summary
    print_summary(results)


if __name__ == "__main__":
    main()

