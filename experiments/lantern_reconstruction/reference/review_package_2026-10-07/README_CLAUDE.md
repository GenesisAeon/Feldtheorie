# Start hier: Lantern-Reaktivierung

1. `LANTERN_FACHREVIEW.md`: Urteil und notwendige Korrekturen.
2. `LANTERN_REAKTIVIERUNG_IMPLEMENTIERUNGSPLAN.md`: vollständiger Auftrag LR0–LR9 mit zwei getrennten Studienprotokollen.
3. `LANTERN_ROADMAP.json` / `.yaml`: identische maschinenlesbare Roadmap; JSON ist maßgeblich.
4. `VERIFICATION_LEDGER.json`: Herkunft, Grenzen und tatsächlich ausgeführte Prüfungen.
5. Zwei Kontrollskripte plus gespeicherte Resultate. Kein Projektmodul und kein Decodertraining wird dadurch ersetzt.

Die sechs alten Planungsdateien bleiben historische Eingaben. Das Paket ist eine neue Fassung, kein stilles Überschreiben dieser Unterlagen. Johanns lokaler Commit ist absichtlich nicht auf GitHub; elf dafür relevante Dateien sind über das Quelleninventar byteidentisch abgeglichen.

## Schnellprüfung

In einer geeigneten bestehenden Python-Umgebung mit NumPy/SciPy/PyYAML:

```bash
python independent_controls.py --output local_control_results.json
python audit_legacy_source.py --source-root D:/mandala/Feldtheorie --output local_source_audit.json
```

Erwartet: 22/22 analytische Kontrollgruppen; drei gepinnte Quellhashes im Quellaudit. Bei Quellabweichung stoppt das Audit absichtlich. Nicht einfach Hashwerte aktualisieren, sondern Unterschiede prüfen und neue Baseline dokumentieren.

`audit_legacy_source.py` führt gezielt ausgewählte vertrauenswürdige Originalmethoden aus dem Quelltext aus; **keinen vollständigen Paketimport**. Unter anderem werden `calculate_impedance` und Konstanten durch die im gelesenen Quelltext bestätigten Werte bereitgestellt. Dies prüft die Kopplungsrechnung, aber weder Registry-Integration noch Import-Isolation. LR1 muss dafür den tatsächlichen lokalen Loader prüfen.

Die gespeicherten Referenzresultate stammen aus Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0. Für das Repo sind dessen unterstützte Abhängigkeitsgrenzen maßgeblich, keine globale Aktualisierung erforderlich. Numerische Toleranzen statt plattformübergreifender Bitgleichheit verwenden.

## Ausführen in sinnvoller Reihenfolge

Zuerst LR0–LR5 implementieren und verifizieren. LR6 liefert den konkreten Freeze-Kandidaten. Bis dahin nur Entwicklung und Smoke, keine bestätigende Forschungsrechnung. Optionale MLP-Arbeiten dürfen den Ridge-Kern nicht blockieren. Prozessrauschen und assoziatives Abrufen bleiben LR9-Folgestudien.

SCF ist erst ein möglicher Berichtadapter in LR8. Kein neuer Frameworkzwang und keine Änderungen an den eingefrorenen Mandala-Runden. Der Original-Lanternkern bleibt Referenz. Gepaarte Vergleiche und die Trennung von Inhalt, Dynamik und Beobachtung sind verpflichtend.

Eine grüne Prüfung bestätigt die jeweils getestete Eigenschaft. 22/22 Kontrollen bedeutet nicht „das Lantern-Netz besitzt ein bewiesenes Gedächtnis“. Ein negativer Forschungsbefund ist ein zulässiger Projektabschluss.

`SHA256SUMS.txt` enthält die Hashes aller übrigen Dateien dieses Pakets; die Hashliste und das ZIP hashen sich nicht selbst.
