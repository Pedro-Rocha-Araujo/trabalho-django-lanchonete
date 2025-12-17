from django.db import models

# Classe Cliente
class Cliente(models.Model):
    nome = models.CharField(max_length=50)
    telefone = models.CharField(max_length=20)

# Classe Funcionario
class Funcionario(models.Model):
    nome = models.CharField(max_length=50)
    especialidade = models.CharField(max_length=255)

# Classe Serviço
class Lanche(models.Model):
    nome = models.CharField(max_length=50)
    valor = models.DecimalField(max_digits=5, decimal_places=2)

# Classe Andamento do Serviço
class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE)
    # lanche = models.ForeignKey(Lanche, on_delete=models.CASCADE)
    data = models.DateField()


# Classe Item Pedido
class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    lanche = models.ForeignKey(Lanche, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.lanche.valor * self.quantidade

# Classe Pagamento
class Pagamento(models.Model):
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=6, decimal_places=2)
    pago = models.BooleanField(default=False)
