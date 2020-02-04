(function(){
    var cardContainer = document.getElementById('stripe-card-element');
    var stripe = Stripe(cardContainer.getAttribute('data-public-key'));
    var elements = stripe.elements();

    var card = elements.create('card', {
        style: {
            base: {
                lineHeight: 2
            }
        },
        classes: {
            base: 'input',
            focus: 'focus',
        }
    });
    card.mount('#stripe-card-element');

    card.addEventListener('change', function(e) {
        if (e.error) {

        } else {

        }
    });

    var form = document.getElementById('add-card-form');
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        stripe.createToken(card).then(function(res) {
            if (res.error) {

            } else {
                var input = document.createElement('input');
                input.setAttribute('type', 'hidden');
                input.setAttribute('name', 'stripe_token');
                input.setAttribute('value', res.token.id);

                form.appendChild(input);

                form.submit();
            }
        });
    });
})();
