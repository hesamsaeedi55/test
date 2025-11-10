import SwiftUI



struct AddressView: View {

    

    let width = UIScreen.main.bounds.width

    let height = UIScreen.main.bounds.height

    

    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject var AdrsViewModel: AddressViewModel
    @EnvironmentObject var categoryVM: CategoryViewModel

    @State var addingAddressAllowed = true

    @State var creatingAddressStatus: Bool = false

    @State var addbuttonTapped: Bool = false

    @State var alertMessageIsActive : Bool = false

    @State var isDeleteConfirmationPresented : Bool = false

    @State var addressToDelete: Address?
    
    @State var deleteErrorMessage: String?
    @State var showDeleteErrorAlert: Bool = false

    

    @EnvironmentObject var navigationVM: NavigationStackManager

    

    init(previewData: AddressViewModel? = nil) {

        // Note: For previews only, we can't use @EnvironmentObject in init

        // The preview will need to provide the environment object separately

    }

    

    var body: some View {

        

        ZStack {

            

            

            //                Color(hex: "8A8077")

            //

            //                    .ignoresSafeArea()

            VStack(spacing: 0) {

                

                navigationBar()

                    .padding(.bottom)

                GeometryReader { geo in

                    

                     

                    ScrollView {

                        

                        VStack(spacing:height/40) {

                            

                            addressStack()

                            

                            .alert(Text("آدرس حذف بشه؟"), isPresented: $isDeleteConfirmationPresented) {

                                

                                Button {

                                    

                                    

                                    

                                }label:{

                                    Text("نه")

                                }

                                Button {

                                    Task {

                                        do {

                                            try await AdrsViewModel.deleteaddress(address: addressToDelete!)

                                            // Success - dismiss confirmation dialog

                                            isDeleteConfirmationPresented = false

                                        } catch let error as NSError {

                                            // Extract error message from NSError

                                            let errorMessage = error.userInfo[NSLocalizedDescriptionKey] as? String ?? error.localizedDescription

                                            

                                            // Handle specific error codes

                                            switch error.code {

                                            case 1:

                                                deleteErrorMessage = "آدرس معتبر نیست. لطفا دوباره تلاش کنید."

                                            case 2:

                                                deleteErrorMessage = "خطا در اتصال به سرور. لطفا دوباره تلاش کنید."

                                            case -1001:

                                                deleteErrorMessage = "درخواست شما زمان بر شد. لطفا دوباره تلاش کنید."

                                            case -1009:

                                                deleteErrorMessage = "اتصال اینترنت برقرار نیست. لطفا اتصال خود را بررسی کنید."

                                            case 401, 403:

                                                deleteErrorMessage = "دسترسی شما به این عملیات مجاز نیست."

                                            case 404:

                                                deleteErrorMessage = "آدرس یافت نشد."

                                            case 500...599:

                                                deleteErrorMessage = "خطای سرور. لطفا بعدا تلاش کنید."

                                            default:

                                                deleteErrorMessage = errorMessage

                                            }

                                            

                                            // Show error alert

                                            await MainActor.run {

                                                showDeleteErrorAlert = true

                                                isDeleteConfirmationPresented = false

                                            }

                                        } catch {

                                            // Handle any other errors

                                            await MainActor.run {

                                                deleteErrorMessage = "خطای غیرمنتظره: \(error.localizedDescription)"

                                                showDeleteErrorAlert = true

                                                isDeleteConfirmationPresented = false

                                            }

                                        }

                                    }

                                }label:{

                                    Text("آره")

                                    

                                }

                            }
                            .alert("خطا", isPresented: $showDeleteErrorAlert) {
                                Button("باشه", role: .cancel) {
                                    deleteErrorMessage = nil
                                }
                            } message: {
                                if let errorMessage = deleteErrorMessage {
                                    Text(errorMessage)
                                }
                            }

                            

                        }

                        

                      

                        

                        

                        

                       

                    }.padding(.top, geo.size.height / 180)

                }

            }

        }

            .ignoresSafeArea()

        

        

    }

    

    @ViewBuilder

    func addressStack() -> some View {

        if let addresses = AdrsViewModel.addressesArray {

            

            ForEach(addresses, id: \.id) { address in

                

                

                VStack(spacing:0) {

                    HStack { 

                        

                        Button {

                            

                            let addressDetailView = AddressDetailView(address: address).environmentObject(navigationVM)

                            

                            navigationVM.pushView(addressDetailView)

                            

                        }label:{

                            

                            

                            Image("pencil")

                                .resizable()

                                .frame(width: 50, height: 50)

                                .padding(.leading)

                            

                        }

                        Spacer()

                        

                        Text("عنوان: \(address.label)")

                            .font(.custom("DoranNoEn", size: 18))

                            .padding(12)

                            .foregroundStyle(.black)

                    }

                    VStack(spacing:0) {

                        HStack {

                            Spacer()

                            

                            Text("نام گیرنده: \(address.receiver_name)")

                                .font(.custom("DoranNoEn", size: 14))

                                .foregroundStyle(.black)

                                .shadow(radius: 3)

                                .padding(.trailing,12)

                                .multilineTextAlignment(.trailing)

                        }

                        HStack {

                            Spacer()

                            

                            Text("آدرس: \(address.street_address)")

                                .font(.custom("DoranNoEn", size: 14))

                                .foregroundStyle(.black)

                                .shadow(radius: 3)

                                .padding(.trailing,12)

                                .multilineTextAlignment(.trailing)

                            

                        }

                        HStack {

                            Spacer()

                            

                            Text("تلفن: \(address.phone.persianDigits)")

                                .font(.custom("DoranNoEn", size: 14))

                                .foregroundStyle(.black)

                                .shadow(radius: 3)

                                .padding(.trailing,12)

                                .multilineTextAlignment(.trailing)

                        }

                        HStack {

                            Spacer()

                            

                            Text("کدپستی: \(address.postal_code)")

                                .font(.custom("DoranNoEn", size: 14))

                                .foregroundStyle(.black)

                                .shadow(radius: 3)

                                .padding(.trailing,12)

                                .multilineTextAlignment(.trailing)

                                .padding(.bottom,12)

                            

                        }

                        

                    }

                    HStack {

                        Button {

                            

                            addressToDelete = address

                            isDeleteConfirmationPresented = true

                            

                            

                        }label:{

                            Text("حذف")

                                .font(.custom("DoranNoEn-Bold", size: 14))

                                .foregroundStyle(.red)

                                .shadow(radius: 3)

                                .padding(.leading,12)

                                .multilineTextAlignment(.trailing)

                                .padding(.bottom,12)

                                .clipped()

                                .frame(width:60)

                        }

                        Spacer()

                    }

                }

                .background(CustomBlurView(effect: .systemUltraThinMaterial))

                .frame(maxWidth: .infinity)

                .cornerRadius(12)

                .padding(.horizontal)

                

                .onAppear {

                    if addresses.count == 3 {

                        print(addresses.count)

                        addingAddressAllowed = false

                    }

                }

                .onChange(of: addresses.count) { newValue in

                    

                    if newValue <= 2 {

                        addingAddressAllowed = true

                    }

                }

            }

        }

    }

   

  

    @ViewBuilder

    func navigationBar() -> some View {

        

        VStack {

            Spacer()

            

            HStack(alignment:.bottom) {

                

                HStack {

                    Button(action: {

                        

                        navigationVM.popView(from:.profile)

                        

                    }) {

                        Image(systemName: "chevron.left.circle.fill")

                            .resizable()

                            .frame(width: width/16, height: width/16)

                            .foregroundStyle(.black)

                    }

                    Spacer()

                }

                .frame(width: width/4.4, height: width/18)

                .padding(.leading,width/18)

                .padding(.bottom,10)

                

                

                Spacer()

                

                

                Text("آدرس های من")

                    .font(.custom("DoranNoEn-Bold", size: 20))

                

                Spacer()

                

                Button {

                    

                    print(AdrsViewModel.addressesArray?.count ?? 0)

                    if let count = AdrsViewModel.addressesArray?.count, count < 3 {

                        

                        if addingAddressAllowed {

                            AdrsViewModel.creatingAddressMode = true

                            addbuttonTapped = true

                        }

                    }else{

                        alertMessageIsActive = true

                    }

                    

                    

                }label:{

                    Text("افزودن آدرس")

                        .font(.custom("DoranNoEn-Bold", size: 16))

                        .frame(width: width/4.4, height: width/18)

                }

                .padding(.trailing,width/18)

                

                .alert("نمی توانید بیش از ۳ آدرس داشته باشید", isPresented: $alertMessageIsActive) {

                    Text("باشه")

                }

                

                 

                .onAppear {

                    // Always reload addresses to get fresh data from server

                    Task {

                        do {

                            try await AdrsViewModel.loadAddress()

                        }catch{

                            // Silently handle errors - addresses might already be loaded

                        }

                    }

                }

                

                .navigationDestination(isPresented: $addbuttonTapped ) {

                    

                    if addingAddressAllowed {

                        AddressDetailView(address: Address(

                            id: 0,

                            label: "",

                            receiver_name: "",

                            country: "ایران",

                            state: "",

                            city: "",

                            street_address: "",

                            unit: "",

                            postal_code: "",

                            phone: "",

                            full_address: ""

                        ))

                    }

                }

                .navigationBarBackButtonHidden(true)

                .ignoresSafeArea()

                

            }

            .padding(.bottom,2)

            

        }

        .frame(height: height/9 )

        .background(CustomBlurView(effect: .systemThinMaterial))

    }

}

   

    

 

#Preview {

    AddressView()

        .environmentObject(AddressViewModel.exampleAddress)

        .environmentObject(NavigationStackManager())

        .environmentObject(CategoryViewModel())

}

extension AddressViewModel {

    static let exampleAddress: AddressViewModel = {

        let vm = AddressViewModel()

        vm.addressesArray = [

            Address(id: 1, label: "خانه", receiver_name: "لئو مسی", country: "ایران", state: "تهران", city: "تهران", street_address: "خیابان ولیعصر", unit: "پلاک ۱۲", postal_code: "1234567890", phone: "09123456789", full_address: "تهران، خیابان ولیعصر، پلاک ۱۲"),

            Address(id: 2, label: "دفتر", receiver_name: "مایک اینگلس", country: "ایران", state: "تهران", city: "تهران", street_address: "خیابان نیاوران - کوچه وایب", unit: "ساختمان ۵", postal_code: "0987654321", phone: "09123456789", full_address: "تهران، خیابان انقلاب، ساختمان ۵")

        ]

        return vm

    }()

}

