def calculate_change(
    current_price,
    previous_price,
    current_volume,
    average_volume,
):
    reasons = []
    score = 0

    # -------------------------
    # Price change
    # -------------------------
    if previous_price and previous_price > 0:
        price_change = (
            (current_price - previous_price)
            / previous_price
        ) * 100
    else:
        price_change = 0

    abs_price_change = abs(price_change)

    if abs_price_change >= 5:
        score += 40
        reasons.append(
            f"Large price movement of {price_change:.2f}%"
        )

    elif abs_price_change >= 3:
        score += 25
        reasons.append(
            f"Significant price movement of {price_change:.2f}%"
        )

    elif abs_price_change >= 1.5:
        score += 10
        reasons.append(
            f"Price moved {price_change:.2f}%"
        )

    # -------------------------
    # Volume change
    # -------------------------
    if average_volume > 0:
        volume_ratio = current_volume / average_volume
    else:
        volume_ratio = 1

    if volume_ratio >= 3:
        score += 35
        reasons.append(
            f"Unusual trading volume ({volume_ratio:.1f}x normal)"
        )

    elif volume_ratio >= 2:
        score += 25
        reasons.append(
            f"High trading volume ({volume_ratio:.1f}x normal)"
        )

    elif volume_ratio >= 1.5:
        score += 10
        reasons.append(
            f"Above-normal trading volume ({volume_ratio:.1f}x)"
        )

    # -------------------------
    # Severity
    # -------------------------
    if score >= 70:
        severity = "HIGH"

    elif score >= 40:
        severity = "MEDIUM"

    elif score >= 15:
        severity = "LOW"

    else:
        severity = "NORMAL"

    return {
        "price_change_percent": round(price_change, 2),
        "volume_ratio": round(volume_ratio, 2),
        "change_score": score,
        "severity": severity,
        "reasons": reasons
    }