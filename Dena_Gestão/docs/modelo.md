# Modelo inicial do banco de dados

## Entidades do MVP

- Usuário
- Categoria
- Produto
- Variação de Produto
- Cliente
- Pedido
- Item do Pedido
- Pagamento
- Movimentação de Estoque

## Relacionamentos

- Uma categoria possui vários produtos.
- Um produto possui várias variações.
- Um cliente possui vários pedidos.
- Um pedido possui vários itens.
- Um item do pedido referencia uma variação de produto.
- Um pedido pode possuir um ou mais pagamentos.
- Uma variação de produto possui várias movimentações de estoque.

## Categoria

- id
- nome
- descricao
- status
- data_criacao

## Produto

- id
- categoria_id
- nome
- descricao
- preco_padrao
- custo_estimado
- personalizado
- possui_bordado
- imagem
- status
- data_criacao
- data_atualizacao

## Variação de Produto

- id
- produto_id
- tamanho
- cor
- modelo
- codigo_sku
- quantidade_estoque
- estoque_minimo
- status

## Cliente

- id
- nome
- telefone
- email
- status
- data_criacao

## Pedido

- id
- cliente_id
- numero_pedido
- status
- data_pedido
- data_prevista_entrega
- valor_bruto
- desconto
- taxas
- valor_liquido
- observacoes

## Item do Pedido

- id
- pedido_id
- variacao_produto_id
- quantidade
- preco_unitario
- desconto
- subtotal

## Pagamento

- id
- pedido_id
- forma_pagamento
- status
- valor_bruto
- taxa
- valor_liquido
- data_pagamento

## Movimentação de Estoque

- id
- variacao_produto_id
- tipo
- quantidade
- motivo
- data_movimentacao
- usuario_id