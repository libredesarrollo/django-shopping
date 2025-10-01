<div class="container mx-auto px-4 py-8 lg:px-8">
    <div class="lg:grid lg:grid-cols-4 lg:gap-8">
        <aside class="mb-8 lg:mb-0">
            <div class="sticky top-24">
                <h2 class="text-lg font-semibold text-gray-900 dark:text-white">{{ __('Filters') }}</h2>
                <div class="mt-4 space-y-6">
                    <div>
                        <label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
                            for="search">{{ __('Search') }}</label>
                        <div class="relative">
                        
                            <input
                                class="form-input w-full rounded-md border-gray-200 bg-white py-2.5 pl-10 pr-4 text-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-gray-800 dark:border-gray-700 dark:text-white"
                                id="search" wire:model.debounce.500ms="search" placeholder="{{ __('Search products') }}..."
                                type="search" />
                        </div>
                    </div>
                    <div>
                        <label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
                            for="category">{{ __('Category') }}</label>
                        <select
                            class="form-select w-full rounded-md border-gray-200 bg-white text-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-gray-800 dark:border-gray-700 dark:text-white"
                            id="category" wire:model.live="category_id">
                            <option value="">{{ __('All') }}</option>
                            @foreach ($categories as $i => $c)
                                <option value="{{ $i }}">{{ $c }}</option>
                            @endforeach
                        </select>
                    </div>
                    <div>
                        <label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">{{ __('Tag') }}</label>
                        <div class="flex flex-wrap gap-2">
                            @foreach ($tags as $i => $t)
                                <button wire:click="$set('tag_id', {{ $i }})"
                                    class="rounded-full border px-3 py-1 text-sm transition-colors {{ $tag_id == $i ? 'border-primary-500 bg-primary-50 text-primary-600 font-medium' : 'border-gray-200 text-gray-600 hover:border-primary-500 hover:bg-primary-50 hover:text-primary-600 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800' }}">
                                    {{ $t }}
                                </button>
                            @endforeach
                        </div>
                    </div>
                    <div>
                        <label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
                            for="language">{{ __('Language') }}</label>
                        <select
                            class="form-select w-full rounded-md border-gray-200 bg-white text-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-gray-800 dark:border-gray-700 dark:text-white"
                            id="language" wire:model.live='language'>
                            <option value="">{{ __('All') }}</option>
                            <option value="english">{{ __('English') }}</option>
                            <option value="spanish">{{ __('Spanish') }}</option>
                        </select>
                    </div>
                    <div>
                        <label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">{{ __('Date Range') }}</label>
                        <div class="grid grid-cols-2 gap-2">
                            <input
                                class="form-input w-full rounded-md border-gray-200 bg-white text-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-gray-800 dark:border-gray-700 dark:text-white"
                                type="date" wire:model.live="from" placeholder="{{ __('From') }}" />
                            <input
                                class="form-input w-full rounded-md border-gray-200 bg-white text-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-gray-800 dark:border-gray-700 dark:text-white"
                                type="date" wire:model.live="to" placeholder="{{ __('To') }}" />
                        </div>
                    </div>
                </div>
            </div>
        </aside>

        <div class="lg:col-span-3">
            <div class="mb-8 flex flex-wrap items-center justify-between gap-4">
                <h1 class="text-4xl font-bold text-gray-900 dark:text-white">
                    {{ $productType ? $productType->title : __('All Products') }}
                </h1>
                {{-- You can add a sort-by dropdown here if needed --}}
            </div>

            @if ($productType && View::exists('livewire.store.product.partials.list.' . $productType->slug))
                @include('livewire.store.product.partials.list.' . $productType->slug)
            @else
                <div class="grid grid-cols-2 gap-x-4 gap-y-8 md:grid-cols-3">
                    @forelse ($products as $p)
                        <a href="{{ route('s.p.show', ['productType' => $p->productType->slug, 'product' => $p->slug]) }}"
                            class="group relative flex cursor-pointer flex-col">
                            <div class="relative mb-3 overflow-hidden rounded-md">
                                <div class="aspect-[3/4] w-full bg-cover bg-center bg-no-repeat transition-transform duration-300 group-hover:scale-105"
                                    style="background-image: url('{{ $p->getImageUrl() }}'); view-transition-name: {{ $p->slug }}">
                                </div>
                                {{-- Favorite button can be added here --}}
                            </div>
                            <div>
                                <h3
                                    class="text-sm font-semibold text-gray-800 group-hover:text-primary-600 dark:text-gray-200 dark:group-hover:text-primary-400">
                                    {{ $p->title }}</h3>
                                <p class="text-sm font-medium text-gray-500 dark:text-gray-300 ml-3">{{ $p->price_offert }}$</p>
                            </div>
                        </a>
                    @empty
                        <div class="col-span-full text-center text-gray-500 dark:text-gray-400">
                            <p>{{ __('No products found.') }}</p>
                        </div>
                    @endforelse
                </div>
            @endif
            <div class="mt-8">
                {{ $products->links() }}
            </div>
        </div>
    </div>
</div>
