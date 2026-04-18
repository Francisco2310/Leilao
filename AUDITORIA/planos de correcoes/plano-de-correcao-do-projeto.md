# Plano de Correcao do Projeto

## Objetivo

Registrar um plano pratico, faseado e executavel para corrigir os problemas identificados no dominio de leiloes, reduzir ambiguidade de regra de negocio e estabilizar o setup do projeto.

Este plano foi montado para servir como trilha de execucao. A ordem abaixo prioriza risco de negocio primeiro, depois consistencia temporal e, por fim, setup e manutencao.

## Resumo Executivo

Os pontos mais sensiveis hoje estao em `domain/Entities/auction.py`, porque as regras centrais de lance, moeda e encerramento estao concentradas ali.

Ordem recomendada:

1. Corrigir regra de valor minimo e moeda do leilao.
2. Corrigir regras temporais de expiracao e fechamento.
3. Fechar lacunas de teste.
4. Ajustar setup do projeto e documentacao.

## Fase 0 - Alinhamento de Regra de Negocio

### Objetivo

Eliminar ambiguidade antes de refatorar a entidade principal.

### Onde aplicar

- Arquivo de referencia desta decisao: `AUDITORIA/planos de correcoes/plano-de-correcao-do-projeto.md`
- Implementacao futura: `domain/Entities/auction.py`
- Testes futuros: `domain/Entities/test_auction.py`

### Decisoes que precisam ficar oficiais

1. `minimum_bid` significa:
   - opcao recomendada: lance minimo de entrada no leilao
   - opcao alternativa: preco de reserva para fechamento
2. O leilao pode ser fechado manualmente antes de `expires_at`?
   - recomendacao: nao, exceto se no futuro existir uma acao administrativa separada
3. No instante exato de `expires_at`, ainda aceita lance?
   - recomendacao: nao
4. O leilao aceita moedas diferentes?
   - recomendacao: nao

### Direcao recomendada

Adotar estas regras como padrao do projeto:

- `minimum_bid` passa a valer para o primeiro lance aceito.
- Todos os lances devem ter a mesma moeda do leilao.
- O leilao nao recebe lance em `expires_at` nem depois.
- O metodo `close()` so fecha automaticamente apos expirar.

### Criterio de saida da fase

As quatro decisoes acima devem ser tratadas como regra oficial para guiar as fases seguintes.

## Fase 1 - Corrigir Regra de Lance Minimo e Moeda

### Objetivo

Corrigir o nucleo da regra de negocio para que o leilao aceite apenas lances coerentes com o minimo configurado e com a moeda do leilao.

### Onde aplicar

- `domain/Entities/auction.py`
- `domain/Exceptions/domain_exceptions.py`
- `domain/Entities/test_auction.py`
- Opcionalmente `domain/ValueObjects/test_money.py` se a validacao de moeda ganhar cobertura complementar

### Problemas que esta fase resolve

- Primeiro lance abaixo do valor minimo do leilao ainda pode entrar.
- Lances em moedas diferentes podem ser aceitos no fluxo de entrada.
- A falha de moeda tende a aparecer tarde, no fechamento, em vez de ser barrada na origem.

### Correcao recomendada

#### 1. Aplicar `minimum_bid` no primeiro lance

Em `domain/Entities/auction.py`, no metodo `add_bid()`:

- substituir a validacao atual do primeiro lance, que hoje compara com `MINIMUM_BID_VALUE`
- passar a comparar o primeiro lance com `self.minimum_bid.amount`

Implementacao esperada:

- se nao houver lances, o primeiro lance deve ser `>= self.minimum_bid.amount`
- se houver lances, manter a regra de superacao do maior lance com base em `minimum_percentage`

#### 2. Bloquear moeda diferente ja no `add_bid()`

Em `domain/Entities/auction.py`, no metodo `add_bid()`:

- validar `bid.value.currency == self.minimum_bid.currency` antes de comparar valores
- se o leilao ja tiver lances, validar tambem consistencia com a moeda do maior lance

Em `domain/Exceptions/domain_exceptions.py`:

- criar uma excecao mais especifica para o dominio, por exemplo `AuctionCurrencyMismatchError`

Recomendacao de design:

- nao reutilizar apenas `CurrencyMismatchError` do value object para o fluxo do leilao
- usar uma excecao de dominio deixa o erro mais claro para camada de aplicacao/API no futuro

### Testes a adicionar ou ajustar

Em `domain/Entities/test_auction.py`:

- adicionar teste para rejeitar primeiro lance abaixo de `minimum_bid`
- adicionar teste para aceitar primeiro lance exatamente igual a `minimum_bid`
- adicionar teste para rejeitar lance com moeda diferente da moeda do leilao
- adicionar teste para rejeitar segundo lance com moeda diferente do primeiro

### Criterio de saida da fase

- Nenhum lance entra com moeda incorreta.
- O primeiro lance respeita o valor minimo configurado.
- Os testes do fluxo de lance cobrem casos validos e invalidos.

## Fase 2 - Corrigir Regras Temporais do Leilao

### Objetivo

Fechar inconsistencias de expiracao e impedir encerramento fora da politica do dominio.

### Onde aplicar

- `domain/Entities/auction.py`
- `domain/Exceptions/domain_exceptions.py`
- `domain/Entities/test_auction.py`

### Problemas que esta fase resolve

- No horario exato de expiracao o sistema ainda aceita lance.
- O leilao pode ser fechado antes do prazo sem regra explicita.

### Correcao recomendada

#### 1. Ajustar borda de expiracao

Em `domain/Entities/auction.py`, no metodo `add_bid()`:

- trocar a regra atual de expiracao de `<` para `<=`

Resultado esperado:

- se `clock.now()` for igual a `expires_at`, o leilao ja esta expirado para fins de lance

#### 2. Impedir fechamento antecipado no `close()`

Em `domain/Entities/auction.py`, no metodo `close()`:

- antes de fechar, validar se `clock.now() >= self.expires_at`
- se ainda nao expirou, lancar uma excecao de dominio especifica

Em `domain/Exceptions/domain_exceptions.py`:

- criar algo como `AuctionNotExpiredError`

Observacao de arquitetura:

- se no futuro houver necessidade de encerrar antes do prazo por moderacao, fraude ou administracao, isso deve existir em outro metodo, nao no `close()` padrao

### Testes a adicionar ou ajustar

Em `domain/Entities/test_auction.py`:

- adicionar teste para rejeitar lance exatamente em `expires_at`
- adicionar teste para rejeitar `close()` antes de `expires_at`
- adicionar teste para permitir `close()` exatamente em `expires_at`
- adicionar teste para permitir `close()` apos `expires_at`

### Criterio de saida da fase

- Nao existe mais ambiguidade na fronteira de tempo.
- `close()` reflete a politica oficial do dominio.

## Fase 3 - Limpeza da Suite e Reforco de Confianca

### Objetivo

Melhorar a qualidade da suite para que ela sirva como rede de seguranca real da refatoracao.

### Onde aplicar

- `domain/Entities/test_auction.py`
- `domain/Entities/test_bid.py`
- `domain/ValueObjects/test_money.py`

### Problemas que esta fase resolve

- Existe teste duplicado com o mesmo nome.
- Algumas regras importantes ainda nao estao cobertas.

### Correcao recomendada

Em `domain/Entities/test_auction.py`:

- remover a duplicacao de `test_cancel_auction_draft`
- reorganizar os testes por bloco de comportamento:
  - criacao e inicio
  - lances
  - expiracao
  - fechamento
  - cancelamento

Recomendacao adicional:

- manter `MockClock` e `MockIdGenerator` no arquivo por enquanto, mas se a suite crescer, mover para fixtures ou helpers de teste

### Testes que devem existir ao final da fase

- primeiro lance abaixo do minimo
- primeiro lance igual ao minimo
- lance com moeda errada
- segundo lance com moeda errada
- lance em `expires_at`
- `close()` antes de expirar
- `close()` em `expires_at`
- `close()` apos expirar

### Criterio de saida da fase

- Suite sem duplicacao silenciosa.
- Regras de negocio principais cobertas por cenarios claros.

## Fase 4 - Ajuste de Setup e Documentacao

### Objetivo

Deixar o projeto reproduzivel para qualquer pessoa que pegar a base.

### Onde aplicar

- `pyproject.toml`
- `README.md`
- Opcionalmente pasta raiz do projeto para arquivos auxiliares de ambiente

### Problemas que esta fase resolve

- `README.md` esta referenciado, mas nao existe.
- O projeto exige Python `>=3.13`, mas o codigo atual aparenta ser compativel com `3.12`.
- Nao ha um passo claro de instalacao e execucao de testes.

### Correcao recomendada

#### 1. Corrigir versao minima do Python

Em `pyproject.toml`:

- se o projeto nao depende de recurso exclusivo de Python 3.13, alterar para `>=3.12`
- se existir decisao de padronizar em 3.13, manter a versao e documentar isso claramente no `README.md`

Minha recomendacao hoje:

- baixar para `>=3.12`, porque o codigo atual compila no ambiente `3.12.3` e isso reduz atrito para desenvolvimento

#### 2. Criar `README.md`

Em `README.md`:

- explicar objetivo do projeto
- descrever estrutura de pastas
- ensinar como instalar dependencias
- ensinar como rodar testes
- documentar regras principais do dominio

#### 3. Revisar dependencias

Em `pyproject.toml`:

- confirmar se `mypy` deve mesmo estar em dependencias principais
- se for apenas ferramenta de desenvolvimento, mover para grupo de dev

### Criterio de saida da fase

- O projeto instala sem surpresa.
- Qualquer pessoa consegue entender o dominio e rodar a validacao local.

## Fase 5 - Validacao Final

### Objetivo

Garantir que o dominio esta consistente apos as correcoes.

### Onde aplicar

- Validacao local na raiz do projeto
- Revisao final dos arquivos alterados nas fases anteriores

### Checklist de validacao

1. Rodar `pytest`
2. Validar que os testes novos falham antes das correcoes e passam depois
3. Validar compilacao do pacote
4. Revisar mensagens de excecao para manter consistencia
5. Revisar nomenclatura de negocio para garantir clareza

### Resultado esperado

- Dominio coerente
- Testes cobrindo as regras mais importantes
- Setup reproduzivel
- Menos risco de ambiguidade funcional

## Ordem de Execucao Recomendada

1. Fase 0 - Alinhamento de regra
2. Fase 1 - Lance minimo e moeda
3. Fase 2 - Regras temporais
4. Fase 3 - Suite de testes
5. Fase 4 - Setup e documentacao
6. Fase 5 - Validacao final

## Primeira Entrega Recomendada

Se quisermos atacar o maior risco primeiro, a primeira entrega deve incluir:

- correcao de `add_bid()` para respeitar `minimum_bid`
- validacao de moeda no leilao
- testes desses dois comportamentos

Isso ja resolve o problema mais perigoso do dominio atual: aceitar lance semanticamente invalido e so explodir tarde demais.
