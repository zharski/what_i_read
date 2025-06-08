"""Statistics module for generating visualizations from links data."""

import json
import logging
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional
import calendar

logger = logging.getLogger(__name__)


class StatsGenerator:
    """Generate statistics and visualizations from links data."""
    
    def __init__(self, data_file: Path = Path("stats/links_with_tags_by_month.json")):
        self.data_file = data_file
        self.data = self._load_data()
        
    def _load_data(self) -> Dict:
        """Load JSON data from file."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Data file not found: {self.data_file}")
            logger.info("Please run the links processor first to generate the data file.")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON file: {e}")
            return {}
    
    def get_links_per_month(self) -> List[Tuple[str, int]]:
        """Get number of links per month in chronological order."""
        monthly_counts = []
        
        for year in sorted(self.data.keys()):
            year_data = self.data[year]
            
            # Create a mapping of month names to month numbers
            month_to_num = {
                f"{month} {year}": i 
                for i, month in enumerate(calendar.month_name) if month
            }
            
            # Sort months by their numeric value
            sorted_months = sorted(
                year_data.items(),
                key=lambda x: month_to_num.get(x[0], 0)
            )
            
            for month_name, links in sorted_months:
                count = len(links)
                # Format as YYYY-MM for x-axis
                month_num = month_to_num.get(month_name, 0)
                if month_num:
                    date_str = f"{year}-{month_num:02d}"
                    monthly_counts.append((date_str, count))
        
        return monthly_counts
    
    def get_tag_frequencies(self) -> Counter:
        """Get frequency count of all tags."""
        tag_counter = Counter()
        
        for year_data in self.data.values():
            for month_links in year_data.values():
                for link in month_links:
                    # Remove # from tags and count them
                    tags = [tag.lstrip('#') for tag in link.get('tags', [])]
                    tag_counter.update(tags)
        
        return tag_counter
    
    def generate_monthly_stats_plot(self, output_file: Path = Path("stats/links_per_month.png")) -> bool:
        """Generate a plot of links per month over time."""
        try:
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            from datetime import datetime
        except ImportError:
            logger.error("matplotlib is required for generating plots.")
            logger.info("Install it with: pip install matplotlib")
            return False
        
        monthly_data = self.get_links_per_month()
        if not monthly_data:
            logger.error("No data available for plotting")
            return False
        
        # Prepare data for plotting
        dates = []
        counts = []
        
        for date_str, count in monthly_data:
            # Convert YYYY-MM to datetime
            year, month = date_str.split('-')
            dates.append(datetime(int(year), int(month), 1))
            counts.append(count)
        
        # Create the plot
        plt.figure(figsize=(14, 8))
        plt.plot(dates, counts, 'b-o', linewidth=2, markersize=6)
        
        # Customize the plot
        plt.title('Number of Links Recorded Over Time', fontsize=16, pad=20)
        plt.xlabel('Time', fontsize=12)
        plt.ylabel('Count', fontsize=12)
        plt.grid(True, alpha=0.3, linestyle='--')
        
        # Format x-axis
        ax = plt.gca()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.xticks(rotation=45)
        
        # Add some padding to y-axis
        y_margin = max(counts) * 0.1
        plt.ylim(0, max(counts) + y_margin)
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Save the plot
        output_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Monthly statistics plot saved to: {output_file}")
        return True
    
    def generate_tag_cloud(self, output_file: Path = Path("stats/tag_cloud.png"), max_tags: int = 100) -> bool:
        """Generate a tag cloud visualization."""
        try:
            from wordcloud import WordCloud
            import matplotlib.pyplot as plt
        except ImportError:
            logger.error("wordcloud is required for generating tag clouds.")
            logger.info("Install it with: pip install wordcloud")
            return False
        
        tag_freq = self.get_tag_frequencies()
        if not tag_freq:
            logger.error("No tags found in the data")
            return False
        
        # Get top tags
        top_tags = dict(tag_freq.most_common(max_tags))
        
        # Create word cloud
        wordcloud = WordCloud(
            width=1200,
            height=600,
            background_color='white',
            colormap='viridis',
            relative_scaling=0.5,
            min_font_size=10
        ).generate_from_frequencies(top_tags)
        
        # Create the plot
        plt.figure(figsize=(15, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(f'Top {len(top_tags)} Tags from Links Collection', fontsize=16, pad=20)
        plt.tight_layout()
        
        # Save the plot
        output_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Tag cloud saved to: {output_file}")
        return True
    
    def print_stats_summary(self):
        """Print summary statistics to console."""
        monthly_data = self.get_links_per_month()
        tag_freq = self.get_tag_frequencies()
        
        if not monthly_data:
            print("No data available.")
            return
        
        print("\n" + "="*50)
        print("LINKS STATISTICS SUMMARY")
        print("="*50)
        
        # Overall stats
        total_links = sum(count for _, count in monthly_data)
        print(f"\nTotal links collected: {total_links}")
        print(f"Total months with data: {len(monthly_data)}")
        print(f"Average links per month: {total_links / len(monthly_data):.1f}")
        
        # Find months with most/least links
        sorted_months = sorted(monthly_data, key=lambda x: x[1])
        print(f"\nMonth with most links: {sorted_months[-1][0]} ({sorted_months[-1][1]} links)")
        print(f"Month with least links: {sorted_months[0][0]} ({sorted_months[0][1]} links)")
        
        # Tag statistics
        print(f"\n\nTAG STATISTICS")
        print("-"*30)
        print(f"Total unique tags: {len(tag_freq)}")
        print(f"Total tag usage: {sum(tag_freq.values())}")
        print(f"Average tags per link: {sum(tag_freq.values()) / total_links:.1f}")
        
        # Top 20 tags
        print(f"\nTop 20 most used tags:")
        for i, (tag, count) in enumerate(tag_freq.most_common(20), 1):
            print(f"{i:2d}. #{tag:<25} ({count} times)")
        
        print("\n" + "="*50) 