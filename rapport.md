# LOG430 - Rapport du laboratoire 06
ÉTS - LOG430 - Architecture logicielle - Hiver 2026 - Groupe 1

Étudiant: Yanni Haddar
Nom github: mapleduck
repo github: https://github.com/mapleduck/log430-labo6-mapleduck

## Questions

> 💡 Question 1 : Lequel de ces fichiers Python représente la logique de la machine à états décrite dans les diagrammes du document arc42? Est-ce que son implémentation est complète ou y a-t-il des éléments qui manquent? Illustrez votre réponse avec des extraits de code.

`order_saga_controller.py` représente la logique de la machine à états. C'est lui qui gère les transitions entre les états définis dans `OrderSagaState`:

```
while self.current_saga_state is not OrderSagaState.END:
    if self.current_saga_state == OrderSagaState.START:
        self.current_saga_state = self.create_order_handler.run()
    elif self.current_saga_state == OrderSagaState.ORDER_CREATED:
        self.decrease_stock_handler = DecreaseStockHandler(...)
        self.current_saga_state = self.decrease_stock_handler.run()
    elif self.current_saga_state == OrderSagaState.STOCK_DECREASED:
        self.create_payment_handler = CreatePaymentHandler(...)
        self.current_saga_state = self.create_payment_handler.run()
    elif self.current_saga_state == OrderSagaState.STOCK_INCREASED:
        self.logger.debug("TODO: implémentez et utilisez la classe DeleteOrderHandler...")
        self.current_saga_state = OrderSagaState.ORDER_DELETED
```

L'implémentation est incomplète, il y a un TODO dans `STOCK_INCERASED`. De plus, `DeleteOrderHandler` ne se fait jamais call car elle n'est pas implémentée. Le controller passe directement à `ORDER_DELETED` sans vraiment le faire.

> 💡 Question 2 : Est-ce que le handler CreateOrderHandler connecte à une base de données directement pour créer des commandes? Illustrez votre réponse 

Non. Il demande à StoreManager de le faire via un call HTTP:

```
def run(self):
    response = requests.post(
        f'{config.API_GATEWAY_URL}/store-manager-api/orders',
        json=self.order_data,
        headers={'Content-Type': 'application/json'}
    )
    if response.ok:
        data = response.json()
        self.order_id = data['order_id'] if data else 0
        return OrderSagaState.ORDER_CREATED
    else:
        return OrderSagaState.END
```

L'orchestrateur ne fait pas de logique ou de data access, il fait juste coordoner les autres services.

> 💡 Question 3 : Quelle requête dans la collection Postman du Labo 05 correspond à l'endpoint appelé par CreateOrderHandler? Illustrez votre réponse avec des captures d'écran ou extraits de code.

C'est la requête POST /orders, qui apelle l'endpoint CreateOrderHandler. Le body correspond.

> 💡 Question 4 : Quel endpoint avez-vous appelé pour modifier le stock? Quelles informations de la commande avez-vous utilisées? Illustrez votre réponse avec des extraits de code.

On fait un POST sur `/store-manager-api/stocks via l'API gateway:
```
response = requests.post(
    f'{config.API_GATEWAY_URL}/store-manager-api/stocks',
    json={
        "items": self.order_item_data,
        "operation": "-"
    },
    headers={'Content-Type': 'application/json'}
)
```

On utilise deux infos de la commande, order_item_data et operation, qui fait en sorte que ca decrease le stock de 1.


> 💡 Question 5 : Quel endpoint avez-vous appelé pour générer une transaction de paiement? Quelles informations de la commande avez-vous utilisées? Illustrez votre réponse avec des extraits de code.

Le premier appel est necessaire pour recuperer le total amount:

```
order_response = requests.get(
    f'{config.API_GATEWAY_URL}/store-manager-api/orders/{self.order_id}',
)
self.total_amount = order_response.json().get('total_amount', 0)
```

Le deuxieme appel premet de creer la transaction:

```
payment_response = requests.post(
    f'{config.API_GATEWAY_URL}/payments-api/payments',
    json={
        "order_id": self.order_id,
        "user_id": self.order_data.get('user_id'),
        "amount": self.total_amount
    }
)
```

> 💡 Question 6 : Quelle est la différence entre appeler l'orchestrateur Saga et appeler directement les endpoints des services individuels? Quels sont les avantages et inconvénients de chaque approche? Illustrez votre réponse avec des captures d'écran ou extraits de code.

<div style="text-align: center;">
  <img src="./img_rapport/image.png" style="width: 75%; padding: 15px;">
</div>

On peut voir sur Jaeger, sur l'icone rouge, que le POST qui diminue les stocks a fail. Le rollback a fonctionne, le delete de compensation a eu lieu. Via un appel direct, il aurait fallu que le client face tout les calls, incluant le rollback si ca fail (ce qui est pas realiste). Saga fait tout tout seul.