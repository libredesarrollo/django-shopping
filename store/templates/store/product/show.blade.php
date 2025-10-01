<div class="py-12">
    @if (View::exists('livewire.store.product.partials.detail.' . $product->productType->slug))
        @include('livewire.store.product.partials.detail.' . $product->productType->slug)
    @else
        <div class="grid grid-cols-1 gap-12 lg:grid-cols-2 lg:gap-16">
            {{-- Columna de la Imagen --}}
            <div class="flex items-start justify-center">
                @if ($product->getImageUrl())
                    <div class="w-full max-w-md overflow-hidden rounded-lg shadow-lg">
                        <img src="{{ $product->getImageUrl() }}" alt="{{ $product->title }}"
                            class="h-full w-full object-cover" style="view-transition-name: {{ $product->slug }}">
                    </div>
                @endif
            </div>

            {{-- Columna de Detalles --}}
            <div class="flex flex-col justify-center">
                <h1 class="text-4xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-5xl">
                    {{ $product->title }}</h1>
                <p class="mt-2 text-xl text-gray-500 dark:text-gray-400">{{ $product->subtitle }}</p>

                <div class="mt-6">
                    <h2 class="sr-only">Product information</h2>
                    <p class="text-3xl tracking-tight text-gray-900 dark:text-white">${{ $product->price_offert }}</p>
                </div>

                <div class="mt-8">
                    <h3 class="text-sm font-medium text-gray-900 dark:text-white">Description</h3>
                    <div class="prose prose-sm mt-4 text-gray-600 dark:text-gray-300">
                        <p>{{ $product->description }}</p>
                    </div>
                </div>

                <div class="mt-8">
                    <div class="flex items-center">
                        <h3 class="text-sm font-medium text-gray-900 dark:text-white">Category:</h3>
                        <a href="{{ route('s.p.index', ['category_id' => $product->post->category->id]) }}"
                            class="ml-2 text-sm text-primary-600 hover:text-primary-500">{{ $product->post->category->title }}</a>
                    </div>
                </div>

                <div class="mt-6">
                    <h3 class="text-sm font-medium text-gray-900 dark:text-white">Tags</h3>
                    <div class="mt-2 flex flex-wrap gap-2">
                        @foreach ($product->tags as $t)
                            <a href="{{ route('s.b.index', ['tag_id' => $t->id]) }}"
                                class="btn-tag">{{ $t->title }}</a>
                        @endforeach
                    </div>
                </div>

                @isset($payment)
                    <x-payments.buyed :payment="$payment" />
                @endisset

                <div class="mt-10">
                    @auth
                        @livewire('store.payment', ['price' => $product->price_offert, 'routeNameSuccessURL' => 's.p.payment', 'cancelURL' => route('s.payment.cancel'), 'productId' => $product->id], key($product->id))
                    @endauth

                    @guest
                        <p class="text-gray-600 dark:text-gray-300">{{ __('You must be authenticated to make the purchase') }}</p>
                        <a href="{{ route('login') }}"
                            class="mt-4 inline-block rounded-md border border-transparent bg-primary-600 px-8 py-3 text-base font-medium text-white hover:bg-primary-700">{{ __('Login') }}</a>
                    @endguest
                </div>
            </div>
        </div>
        <hr class="my-8 border-gray-200 dark:border-gray-700">
        <div class="prose prose-lg max-w-none dark:prose-invert">
            {!! $product->content !!}
        </div>
    @endif
</div>
