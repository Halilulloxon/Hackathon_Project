def analyze_prescription(medicine_name, dosage, instructions):
    text = f'{medicine_name} {dosage} {instructions}'.lower()
    warnings = []
    risk = 'safe'

    danger_words = ['juda ko\'p', 'overdose', '10 tabletka', '20 tabletka', 'spirt', 'alkogol', 'allergiya']
    warning_words = ['antibiotik', 'ukol', 'homilador', 'bola', 'qon bosimi', 'diabet']

    for word in danger_words:
        if word in text:
            risk = 'danger'
            warnings.append(f'Xavfli signal topildi: {word}')
    if risk != 'danger':
        for word in warning_words:
            if word in text:
                risk = 'warning'
                warnings.append(f'Ehtiyotkorlik talab qilinadi: {word}')

    if not dosage.strip():
        risk = 'warning'
        warnings.append('Doza yozilmagan.')
    if len(instructions.strip()) < 10:
        risk = 'warning'
        warnings.append('Qo‘llash tartibi juda qisqa yozilgan.')

    if not warnings:
        warnings.append('AI tahlil: retseptda aniq xavfli signal topilmadi.')

    return risk, '\n'.join(warnings)
