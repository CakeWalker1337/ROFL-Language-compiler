

define i32 @func.f(i32 %x, i32 %y) {
    %x.ptr = alloca i32
    %y.ptr = alloca i32
    store i32 %x, i32* %x.ptr
    store i32 %y, i32* %y.ptr
    %x.1 = load i32, i32* %x.ptr
    %y.2 = load i32, i32* %y.ptr
    %buffer3 = add i32 %x.1, %y.2
    ret i32 %buffer3
}
define i32 @func.f1(i32 %x) {
    %x.ptr = alloca i32
    store i32 %x, i32* %x.ptr
    %f.4 = call i32 @func.f(i32 1, i32 2)
    %x.5 = load i32, i32* %x.ptr
    %buffer6 = add i32 %f.4, %x.5
    ret i32 %buffer6
}

define i32 @main() {
    %f1.7 = call i32 @func.f1(i32 3)
    %buffer9 = getelementptr inbounds [4 x i8], [4 x i8]* @.str.1, i32 0, i32 0 
    call i32 (i8*, ...) @printf(i8* %buffer9, i32 %f1.7)
    ret i32 0
}

declare i32 @printf(i8*, ...)
@.str.1 = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
