from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    nome_exibicao = models.CharField(max_length=200, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.nome_exibicao or self.username


class Escola(models.Model):
    ORIGEM_CHOICES = [
        ('sistema', 'Sistema'),
        ('manual', 'Manual'),
    ]

    nome_oficial = models.CharField(max_length=300)
    nome_usual = models.CharField(max_length=300, blank=True)
    diretor = models.CharField(max_length=200, blank=True)
    mediador = models.CharField(max_length=200, blank=True)
    endereco = models.CharField(max_length=500, blank=True)
    cep = models.CharField(max_length=20, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    origem = models.CharField(max_length=20, choices=ORIGEM_CHOICES, default='sistema')
    bloco_1 = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome_oficial']
        verbose_name = 'Escola'
        verbose_name_plural = 'Escolas'

    def __str__(self):
        return self.nome_usual or self.nome_oficial

    def to_dict(self):
        return {
            'id': self.pk,
            'nome_oficial': self.nome_oficial,
            'nome_usual': self.nome_usual,
            'diretor': self.diretor,
            'mediador': self.mediador,
            'endereco': self.endereco,
            'cep': self.cep,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'origem': self.origem,
            'bloco_1': self.bloco_1,
            'ativo': self.ativo,
        }


class Mediador(models.Model):
    nome = models.CharField(max_length=200)
    escola = models.ForeignKey(
        Escola, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='mediadores'
    )
    escola_nome = models.CharField(max_length=300, blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Mediador'
        verbose_name_plural = 'Mediadores'

    def __str__(self):
        return self.nome

    def to_dict(self):
        return {
            'id': self.pk,
            'nome': self.nome,
            'escola_id': self.escola_id,
            'escola_nome': self.escola_nome,
            'ativo': self.ativo,
        }


class Visita(models.Model):
    TURNO_CHOICES = [
        ('manha', 'Manhã'),
        ('tarde', 'Tarde'),
        ('integral', 'Integral'),
    ]

    escola = models.ForeignKey(
        Escola, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='visitas'
    )
    escola_nome = models.CharField(max_length=300, blank=True)
    escola_nome_oficial = models.CharField(max_length=300, blank=True)
    data = models.DateField()
    hora = models.TimeField(null=True, blank=True)
    turno = models.CharField(max_length=20, choices=TURNO_CHOICES, blank=True)
    oficina = models.CharField(max_length=500, blank=True)
    observacoes = models.TextField(blank=True)
    contribuicoes = models.TextField(blank=True)
    combinados = models.TextField(blank=True)
    mediador_nome = models.CharField(max_length=200, blank=True)
    articulador_nome = models.CharField(max_length=200, blank=True)
    gestor_nome = models.CharField(max_length=200, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data', '-criado_em']
        verbose_name = 'Visita'
        verbose_name_plural = 'Visitas'

    def __str__(self):
        return f"{self.escola_nome} - {self.data}"

    def to_dict(self):
        turmas = list(self.turmas.values(
            'id', 'nome_turma', 'quantidade', 'nivel', 'avaliacao', 'faixa_etaria'
        ))
        anexos = [
            {
                'id': a.pk,
                'caminho': a.arquivo.name if a.arquivo else '',
                'tipo': a.tipo,
                'nome_original': a.nome_original,
            }
            for a in self.anexos.all()
        ]
        return {
            'id': self.pk,
            'escola_id': self.escola_id,
            'escola_nome': self.escola_nome,
            'escola_nome_oficial': self.escola_nome_oficial,
            'data': str(self.data),
            'hora': str(self.hora) if self.hora else None,
            'turno': self.turno,
            'oficina': self.oficina,
            'observacoes': self.observacoes,
            'contribuicoes': self.contribuicoes,
            'combinados': self.combinados,
            'mediador_nome': self.mediador_nome,
            'articulador_nome': self.articulador_nome,
            'gestor_nome': self.gestor_nome,
            'turmas': turmas,
            'anexos': anexos,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None,
        }


class TurmaVisita(models.Model):
    visita = models.ForeignKey(Visita, on_delete=models.CASCADE, related_name='turmas')
    nome_turma = models.CharField(max_length=200, blank=True)
    quantidade = models.IntegerField(null=True, blank=True)
    nivel = models.CharField(max_length=200, blank=True)
    avaliacao = models.CharField(max_length=50, blank=True)
    faixa_etaria = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'Turma da Visita'
        verbose_name_plural = 'Turmas das Visitas'


class AnexoVisita(models.Model):
    visita = models.ForeignKey(Visita, on_delete=models.CASCADE, related_name='anexos')
    arquivo = models.FileField(upload_to='uploads/', blank=True)
    tipo = models.CharField(max_length=50, blank=True)
    nome_original = models.CharField(max_length=500, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Anexo de Visita'
        verbose_name_plural = 'Anexos de Visitas'

    def __str__(self):
        return self.nome_original


class Evento(models.Model):
    TIPO_CHOICES = [
        ('visita', 'Visita'),
        ('reuniao', 'Reunião'),
        ('feriado', 'Feriado'),
        ('apresentacao', 'Apresentação'),
        ('capacitacao', 'Capacitação'),
        ('outro', 'Outro'),
    ]
    STATUS_CHOICES = [
        ('planejado', 'Planejado'),
        ('executado', 'Executado'),
        ('cancelado', 'Cancelado'),
    ]
    TURNO_CHOICES = [
        ('manha', 'Manhã'),
        ('tarde', 'Tarde'),
        ('integral', 'Integral'),
    ]

    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, default='outro')
    titulo = models.CharField(max_length=500)
    data = models.DateField()
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fim = models.TimeField(null=True, blank=True)
    turno = models.CharField(max_length=20, choices=TURNO_CHOICES, blank=True)
    dia_inteiro = models.BooleanField(default=False)
    escola = models.ForeignKey(
        Escola, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='eventos'
    )
    escola_nome = models.CharField(max_length=300, blank=True)
    local = models.CharField(max_length=500, blank=True)
    descricao = models.TextField(blank=True)
    mediador = models.ForeignKey(
        Mediador, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='eventos'
    )
    mediador_nome = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planejado')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['data', 'hora_inicio']
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'

    def __str__(self):
        return f"{self.titulo} - {self.data}"

    def to_dict(self):
        return {
            'id': str(self.pk),
            'tipo': self.tipo,
            'titulo': self.titulo,
            'data': str(self.data),
            'dia_semana': self.data.weekday() if self.data else None,
            'hora_inicio': str(self.hora_inicio) if self.hora_inicio else None,
            'hora_fim': str(self.hora_fim) if self.hora_fim else None,
            'turno': self.turno,
            'dia_inteiro': self.dia_inteiro,
            'escola_id': self.escola_id,
            'escola_nome': self.escola_nome,
            'local': self.local,
            'descricao': self.descricao,
            'mediador_id': self.mediador_id,
            'mediador_nome': self.mediador_nome,
            'status': self.status,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None,
        }
