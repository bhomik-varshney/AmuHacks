def build_emergency_response(reason: str):

    return {
        "status": "emergency",
        "reason": reason,
        "message": "Immediate external support recommended.",
        "actions":[
            "Stop financial transactions",
            "Contact your bank",
            "Call cybercrime helpline: 1930",
            "Reach a trusted person"
        ]
    }
