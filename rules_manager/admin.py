# rules_manager/admin.py
from django.contrib import admin
from .models import DetectionRule, EditHistory
from django_json_widget.widgets import JSONEditorWidget
from django import forms
from django.core.exceptions import ValidationError
import json

class EditHistoryInline(admin.TabularInline):
    model = EditHistory
    extra = 0
    readonly_fields = ('changed_by', 'change_timestamp', 'changes', 'action_type')
    can_delete = False

class DetectionRuleForm(forms.ModelForm):
    class Meta:
        model = DetectionRule
        fields = "__all__"  # Inclui todos os campos do modelo
        widgets = {
            'rule_data': JSONEditorWidget(options={'mode': 'application/json'}),  # Widget para JSON
        }

    def clean_rule_data(self):
        """Valida a sintaxe JSON do campo rule_data."""
        value = self.cleaned_data.get('rule_data')
        
        # Se o valor for None ou uma string vazia, não faz nada
        if value in (None, ''):
            return value  # Permite valores vazios ou None sem validação adicional
            
        try:
            json.loads(value)  # Verifica se o JSON é válido
        except json.JSONDecodeError:
            raise ValidationError("Conteúdo inválido. Verifique a sintaxe JSON.")
            
        return value  # Retorna o valor, que agora é garantido ser um JSON válido

@admin.register(DetectionRule)
class DetectionRuleAdmin(admin.ModelAdmin):
    form = DetectionRuleForm
    list_display = ('name', 'rule_data', 'created_by', 'created_at', 'updated_at')
    # readonly_fields = ('created_by', 'created_at', 'updated_at')
    search_fields = ['name']
    ordering = ['-created_at']
    inlines = [EditHistoryInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        print("Form fields:", form.base_fields)  # Debug: Exibir campos do formulário
        return form

    def save_model(self, request, obj, form, change):
        """Registro de ações ao salvar o modelo."""
        if not obj.pk:  # Criação de novo registro
            obj.created_by = request.user
            super().save_model(request, obj, form, change)
            EditHistory.objects.create(
                rule=obj,
                changed_by=request.user,
                changes={'name': obj.name, 'rule_data': obj.rule_data},
                action_type='create'
            )
        else:  # Edição de registro existente
            super().save_model(request, obj, form, change)
            EditHistory.objects.create(
                rule=obj,
                changed_by=request.user,
                changes=form.cleaned_data,
                action_type='edit'
            )

    def delete_model(self, request, obj):
        """Registro de deleção do modelo."""
        EditHistory.objects.create(
            rule=obj,
            changed_by=request.user,
            changes={'name': obj.name, 'rule_data': obj.rule_data},
            action_type='delete'
        )
        super().delete_model(request, obj)