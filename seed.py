from crud_operations import CinemaOperations

def seed():
	ops = CinemaOperations()

	# === REGISTI ===
	regista1_id = ops.create_regista("Federico", "Fellini", "Italiana", "1920-01-20")
	regista2_id = ops.create_regista("Christopher", "Nolan", "Britannica", "1970-07-30")

	# === FILM ===
	film1_id = ops.create_film("La Dolce Vita", 174, "Drammatico", "T", 1960, regista1_id)
	film2_id = ops.create_film("Inception", 148, "Fantascienza", "T", 2010, regista2_id)
	film3_id = ops.create_film("Risate Infinite", 90, "Commedia", "T", 2022, regista2_id)

	# === SALE ===
	sala1_id = ops.create_sala(1, 100, "Attiva")
	sala2_id = ops.create_sala(2, 80, "Attiva")

	# === POSTI (solo alcuni per esempio) ===
	for fila in ['A', 'B']:
		for num in range(1, 6):
			ops.create_posto(sala1_id, fila, num)
			ops.create_posto(sala2_id, fila, num)

	# === TECNOLOGIE ===
	tech1_id = ops.create_tecnologia("2D", "Proiezione standard")
	tech2_id = ops.create_tecnologia("3D", "Proiezione tridimensionale")

	# === SUPPORTA (collega tecnologie alle sale) ===
	ops.add_tecnologia_to_sala(sala1_id, tech1_id)
	ops.add_tecnologia_to_sala(sala1_id, tech2_id)
	ops.add_tecnologia_to_sala(sala2_id, tech1_id)

	# === TARIFFE ===
	tariffa1_id = ops.create_tariffa("Standard", 8.00)
	tariffa2_id = ops.create_tariffa("Weekend", 10.00)

	# === OPERATORI ===
	op1_id = ops.create_operatore("Anna", "Verdi", "Cassiere")
	op2_id = ops.create_operatore("Marco", "Blu", "Proiezionista")

	# === CLIENTI ===
	cliente1_id = ops.create_cliente("Mario", "Rossi", "mario.rossi@email.com", "3331234567", "1990-05-10")
	cliente2_id = ops.create_cliente("Luca", "Bianchi", "luca.bianchi@email.com", "3339876543", "1985-11-22")

	# === PROIEZIONI ===
	from datetime import date, time, timedelta, datetime
	oggi = date.today()
	ora1 = time(18, 0)
	ora2 = time(21, 0)
	proiezione1_id = ops.create_proiezione(oggi, ora1, ora2, film1_id, sala1_id, op2_id, tariffa1_id)
	proiezione2_id = ops.create_proiezione(oggi + timedelta(days=1), ora1, ora2, film2_id, sala2_id, op2_id, tariffa2_id)

	# === BIGLIETTI ===
	posti_disp1 = ops.get_posti_disponibili(proiezione1_id)
	posti_disp2 = ops.get_posti_disponibili(proiezione2_id)
	if posti_disp1:
		posto1_id = posti_disp1[0]['ID_Posto']
		ops.create_biglietto(proiezione1_id, cliente1_id, posto1_id)
	if posti_disp2:
		posto2_id = posti_disp2[0]['ID_Posto']
		ops.create_biglietto(proiezione2_id, cliente2_id, posto2_id)

	# === TIPI PROMOZIONE E PROMOZIONI ===
	tipo_promo_id = ops.create_tipo_promozione("Sconto Studenti", "Sconto per studenti universitari")
	promo = ops.create_promozione("Promo Studenti Luglio", tipo_promo_id, 20, oggi, oggi + timedelta(days=30))

	# === RECENSIONI ===
	ops.create_recensione(9, "Film bellissimo!", cliente1_id, film1_id)
	ops.create_recensione(8, "Molto coinvolgente.", cliente2_id, film2_id)

	print("✅ Dati di esempio inseriti!")

if __name__ == "__main__":
	seed()
