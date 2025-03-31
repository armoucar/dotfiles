import click
import pandas as pd
from datetime import datetime
import dateutil.relativedelta
from typing import Dict, Any
from tabulate import tabulate


@click.command()
@click.argument("csv_file", type=click.Path(exists=True))
@click.option(
    "--sort-by",
    "-s",
    type=click.Choice(
        [
            "gross_amount",
            "gross_return",
            "gross_return_percent",
            "tax_amount",
            "net_amount",
            "net_return",
            "net_return_percent",
        ]
    ),
    default="net_return_percent",
    help="Sort results by this metric",
)
@click.option(
    "--descending/--ascending",
    "-d/-a",
    default=True,
    help="Sort order (default: descending)",
)
def compare(csv_file, sort_by, descending):
    """
    Compare multiple investments from a CSV file.

    CSV format: principal,start-date,end-date,annual-rate,tax-rate

    Each row represents a different investment scenario to be compared.
    Dates should be in YYYY-MM-DD format.
    """
    try:
        # Read CSV file into pandas DataFrame
        df = pd.read_csv(csv_file)

        # Check if we have the required columns
        required_cols = ["principal", "start-date", "end-date", "annual-rate", "tax-rate"]
        for col in required_cols:
            if col not in df.columns:
                click.echo(f"Error: Required column '{col}' missing from CSV file.")
                return

        # Convert date columns to datetime
        df["start-date"] = pd.to_datetime(df["start-date"], format="%Y-%m-%d")
        df["end-date"] = pd.to_datetime(df["end-date"], format="%Y-%m-%d")

        # Add investment names
        df["name"] = [f"Investment {i+1}" for i in range(len(df))]

        # Calculate all investment metrics
        results_df = calculate_investments(df)

        # Sort the results
        results_df = results_df.sort_values(by=sort_by, ascending=not descending).reset_index(drop=True)

        # Print comparison table
        print_comparison_table(results_df, sort_by)

    except pd.errors.ParserError as e:
        click.echo(f"Error parsing CSV file: {e}")
    except Exception as e:
        click.echo(f"Error: {e}")


def calculate_investments(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate all metrics for all investments in the DataFrame"""
    # Initialize results DataFrame
    results = []

    # Process each investment
    for idx, row in df.iterrows():
        result = calculate_investment(
            row["name"], row["principal"], row["start-date"], row["end-date"], row["annual-rate"], row["tax-rate"]
        )
        results.append(result)

    # Convert to DataFrame
    return pd.DataFrame(results)


def calculate_investment(
    name: str, principal: float, start_date: datetime, end_date: datetime, annual_rate: float, tax_rate: float
) -> Dict[str, Any]:
    """Calculate all metrics for a single investment"""
    # Convert annual rate to monthly rate
    monthly_rate = (1 + annual_rate / 100) ** (1 / 12) - 1

    # Initialize variables
    current_date = start_date
    current_amount = principal

    # Calculate month by month
    while current_date < end_date:
        # Move to next month
        current_date = current_date + dateutil.relativedelta.relativedelta(months=1)

        # If we've passed the end date, adjust to end date
        if current_date > end_date:
            # Calculate partial month interest based on days
            days_passed = (end_date - (current_date - dateutil.relativedelta.relativedelta(months=1))).days
            days_in_month = (current_date - (current_date - dateutil.relativedelta.relativedelta(months=1))).days
            adjusted_rate = monthly_rate * (days_passed / days_in_month)
            current_date = end_date
            current_amount = current_amount * (1 + adjusted_rate)
        else:
            # Calculate full month interest
            current_amount = current_amount * (1 + monthly_rate)

    # Calculate results
    gross_amount = current_amount
    gross_return = gross_amount - principal
    gross_return_percent = (gross_return / principal) * 100

    tax_amount = gross_return * (tax_rate / 100)
    net_amount = gross_amount - tax_amount
    net_return = net_amount - principal
    net_return_percent = (net_return / principal) * 100

    duration_days = (end_date - start_date).days

    return {
        "name": name,
        "principal": principal,
        "annual_rate": annual_rate,
        "tax_rate": tax_rate,
        "duration_days": duration_days,
        "gross_amount": gross_amount,
        "gross_return": gross_return,
        "gross_return_percent": gross_return_percent,
        "tax_amount": tax_amount,
        "net_amount": net_amount,
        "net_return": net_return,
        "net_return_percent": net_return_percent,
    }


def print_comparison_table(df: pd.DataFrame, sort_by: str) -> None:
    """Print a formatted comparison table using tabulate with pandas DataFrame"""
    # Prepare table headers
    headers = ["Investment", "Principal", "Duration", "Rate", "Gross Amount", "Gross %", "Tax", "Net Amount", "Net %"]

    # Add sort indicator to header
    sort_map = {
        "gross_amount": "Gross Amount",
        "gross_return_percent": "Gross %",
        "tax_amount": "Tax",
        "net_amount": "Net Amount",
        "net_return_percent": "Net %",
    }

    if sort_by in sort_map:
        index = headers.index(sort_map[sort_by])
        headers[index] = f"{headers[index]} ↓"

    # Prepare table rows
    rows = []
    for _, inv in df.iterrows():
        row = [
            inv["name"],
            f"R$ {inv['principal']:,.2f}",
            f"{inv['duration_days']} days",
            f"{inv['annual_rate']:.2f}%",
            f"R$ {inv['gross_amount']:,.2f}",
            f"{inv['gross_return_percent']:.2f}%",
            f"R$ {inv['tax_amount']:,.2f}",
            f"R$ {inv['net_amount']:,.2f}",
            f"{inv['net_return_percent']:.2f}%",
        ]
        rows.append(row)

    # Print the table
    click.echo("")
    click.echo("Investment Comparison")
    click.echo(tabulate(rows, headers, tablefmt="fancy_grid", floatfmt=".2f", numalign="right"))

    # Print insights using pandas analytics
    click.echo("\nInsights:")

    # Best vs worst based on sort criteria
    metric_name = sort_by.replace("_", " ").title()
    difference = abs(df[sort_by].iloc[0] - df[sort_by].iloc[-1])

    if sort_by.endswith("percent"):
        click.echo(f"• Best vs Worst {metric_name}: {difference:.2f} percentage points difference")
    elif sort_by in ("gross_amount", "net_amount", "tax_amount", "gross_return", "net_return"):
        click.echo(f"• Best vs Worst {metric_name}: R$ {difference:,.2f} difference")

    # Calculate average metrics with pandas
    avg_gross_return_pct = df["gross_return_percent"].mean()
    avg_net_return_pct = df["net_return_percent"].mean()

    click.echo(f"• Average Gross Return: {avg_gross_return_pct:.2f}%")
    click.echo(f"• Average Net Return: {avg_net_return_pct:.2f}%")
