# rules_manager/models.py
from django.db import models
from django.contrib.auth import get_user_model
import json

User = get_user_model()

class DetectionRule(models.Model):
    name = models.CharField(max_length=255)
    rule_data = models.TextField(default=json.dumps({}))  # Definindo um dicionário vazio como valor padrão
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class EditHistory(models.Model):
    ACTION_TYPES = [
        ('create', 'Criação'),
        ('edit', 'Edição'),
        ('delete', 'Deleção'),
    ]
    rule = models.ForeignKey(DetectionRule, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    change_timestamp = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField()  # Detalhes das mudanças
    action_type = models.CharField(max_length=10, choices=ACTION_TYPES)

    def __str__(self):
        return f'{self.get_action_type_display()} by {self.changed_by.username} on {self.change_timestamp}'